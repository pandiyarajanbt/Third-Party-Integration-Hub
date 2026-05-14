from django.db import models
from core.models import TimeStampedModel


class PaymentTransaction(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    customer_email = models.EmailField(blank=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.stripe_payment_intent_id} - {self.status}"
