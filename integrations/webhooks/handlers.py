from typing import Callable
from integrations.webhooks.models import WebhookEvent


def handle_stripe(event: WebhookEvent):
    from integrations.payments.handlers import handle_stripe_event
    handle_stripe_event(event.payload)


def handle_twilio(event: WebhookEvent):
    from integrations.sms.handlers import handle_twilio_event
    handle_twilio_event(event.payload)


_HANDLERS: dict[str, Callable] = {
    "stripe": handle_stripe,
    "twilio": handle_twilio,
}


def get_handler(source: str) -> Callable:
    handler = _HANDLERS.get(source)
    if not handler:
        raise ValueError(f"No handler registered for source: {source}")
    return handler
