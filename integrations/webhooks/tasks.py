import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=None, acks_late=True)
def process_webhook_event(self, event_id: str):
    from integrations.webhooks.models import WebhookEvent, DeadLetterEvent
    from integrations.webhooks.handlers import get_handler

    try:
        event = WebhookEvent.objects.get(id=event_id)
    except WebhookEvent.DoesNotExist:
        logger.error("WebhookEvent %s not found", event_id)
        return

    event.status = WebhookEvent.STATUS_PROCESSING
    event.save(update_fields=["status"])

    try:
        handler = get_handler(event.source)
        handler(event)
        event.status = WebhookEvent.STATUS_SUCCESS
        event.save(update_fields=["status"])
        logger.info("Webhook %s processed successfully", event_id)

    except Exception as exc:
        event.retry_count += 1
        event.last_error = str(exc)
        max_retries = settings.WEBHOOK_MAX_RETRIES
        backoff = settings.WEBHOOK_RETRY_BACKOFF

        if event.retry_count >= max_retries:
            event.status = WebhookEvent.STATUS_DEAD
            event.save(update_fields=["status", "retry_count", "last_error"])
            DeadLetterEvent.objects.create(
                webhook_event=event,
                failure_reason=str(exc),
            )
            logger.error("Webhook %s moved to dead-letter after %d retries", event_id, max_retries)
        else:
            delay = backoff * (2 ** (event.retry_count - 1))  # exponential backoff
            event.status = WebhookEvent.STATUS_FAILED
            event.next_retry_at = timezone.now() + timedelta(seconds=delay)
            event.save(update_fields=["status", "retry_count", "last_error", "next_retry_at"])
            raise self.retry(exc=exc, countdown=delay)
