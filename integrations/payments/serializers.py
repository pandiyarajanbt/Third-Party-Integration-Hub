from rest_framework import serializers
from integrations.payments.models import PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "stripe_payment_intent_id", "amount", "currency", "status", "customer_email", "created_at"]
        read_only_fields = ["id", "status", "created_at"]
