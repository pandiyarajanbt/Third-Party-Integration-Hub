import logging
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from integrations.payments.models import PaymentTransaction
from integrations.payments.serializers import PaymentTransactionSerializer

logger = logging.getLogger(__name__)


class CreatePaymentIntentView(APIView):
    def post(self, request):
        amount = request.data.get("amount")
        currency = request.data.get("currency", "usd")
        email = request.data.get("email", "")

        response = requests.post(
            "https://api.stripe.com/v1/payment_intents",
            auth=(settings.STRIPE_SECRET_KEY, ""),
            data={"amount": amount, "currency": currency},
            timeout=10,
        )
        if not response.ok:
            logger.error("Stripe error: %s", response.text)
            return Response({"detail": "Payment gateway error"}, status=502)

        data = response.json()
        transaction = PaymentTransaction.objects.create(
            stripe_payment_intent_id=data["id"],
            amount=amount / 100,
            currency=currency,
            customer_email=email,
        )
        return Response(
            {"client_secret": data["client_secret"], "transaction": PaymentTransactionSerializer(transaction).data},
            status=status.HTTP_201_CREATED,
        )


class PaymentTransactionListView(APIView):
    def get(self, request):
        qs = PaymentTransaction.objects.all().order_by("-created_at")[:50]
        return Response(PaymentTransactionSerializer(qs, many=True).data)
