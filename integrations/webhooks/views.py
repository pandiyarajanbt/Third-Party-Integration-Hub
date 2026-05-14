import hashlib
import hmac
import logging

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.webhooks.models import WebhookEvent
from integrations.webhooks.tasks import process_webhook_event

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        sig_header = request.headers.get("Stripe-Signature", "")
        if not self._verify_stripe_signature(request.body, sig_header):
            return Response({"detail": "Invalid signature"}, status=400)

        payload = request.data
        event = WebhookEvent.objects.create(
            source="stripe",
            event_type=payload.get("type", "unknown"),
            payload=payload,
            headers=dict(request.headers),
        )
        process_webhook_event.delay(str(event.id))
        return Response({"status": "queued"}, status=202)

    def _verify_stripe_signature(self, body: bytes, sig_header: str) -> bool:
        secret = settings.STRIPE_WEBHOOK_SECRET
        if not secret:
            return True  # skip in dev if not configured
        try:
            timestamp = dict(item.split("=") for item in sig_header.split(","))["t"]
            signed_payload = f"{timestamp}.{body.decode()}"
            expected = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, sig_header.split("v1=")[-1].split(",")[0])
        except Exception:
            return False


@method_decorator(csrf_exempt, name="dispatch")
class TwilioWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        event = WebhookEvent.objects.create(
            source="twilio",
            event_type=payload.get("MessageStatus", "unknown"),
            payload=payload,
            headers=dict(request.headers),
        )
        process_webhook_event.delay(str(event.id))
        return Response({"status": "queued"}, status=202)
