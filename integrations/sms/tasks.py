import logging
import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_sms_task(self, sms_id: str):
    from integrations.sms.models import SMSMessage

    sms = SMSMessage.objects.get(id=sms_id)
    try:
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            data={"From": settings.TWILIO_FROM_NUMBER, "To": sms.to_number, "Body": sms.body},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        sms.twilio_sid = data["sid"]
        sms.status = "sent"
        sms.save(update_fields=["twilio_sid", "status"])
        logger.info("SMS %s sent, Twilio SID: %s", sms_id, data["sid"])

    except Exception as exc:
        sms.status = "failed"
        sms.error_message = str(exc)
        sms.save(update_fields=["status", "error_message"])
        raise self.retry(exc=exc)


def handle_twilio_event(payload: dict):
    from integrations.sms.models import SMSMessage

    sid = payload.get("MessageSid")
    status = payload.get("MessageStatus")
    if sid and status:
        SMSMessage.objects.filter(twilio_sid=sid).update(status=status)
        logger.info("Updated SMSMessage %s to %s", sid, status)
