import logging
from integrations.payments.models import PaymentTransaction

logger = logging.getLogger(__name__)

EVENT_STATUS_MAP = {
    "payment_intent.succeeded": "succeeded",
    "payment_intent.payment_failed": "failed",
    "charge.refunded": "refunded",
}


def handle_stripe_event(payload: dict):
    event_type = payload.get("type")
    status = EVENT_STATUS_MAP.get(event_type)
    if not status:
        logger.debug("Unhandled Stripe event type: %s", event_type)
        return

    intent = payload.get("data", {}).get("object", {})
    intent_id = intent.get("id")
    if not intent_id:
        return

    PaymentTransaction.objects.filter(stripe_payment_intent_id=intent_id).update(status=status)
    logger.info("Updated PaymentTransaction %s to %s", intent_id, status)
