from django.urls import path
from integrations.webhooks.views import StripeWebhookView, TwilioWebhookView

urlpatterns = [
    path("stripe/", StripeWebhookView.as_view(), name="webhook-stripe"),
    path("twilio/", TwilioWebhookView.as_view(), name="webhook-twilio"),
]
