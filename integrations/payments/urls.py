from django.urls import path
from integrations.payments.views import CreatePaymentIntentView, PaymentTransactionListView

urlpatterns = [
    path("intents/", CreatePaymentIntentView.as_view(), name="payment-create"),
    path("transactions/", PaymentTransactionListView.as_view(), name="payment-list"),
]
