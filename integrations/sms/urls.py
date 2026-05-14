from django.urls import path
from integrations.sms.views import SendSMSView

urlpatterns = [
    path("send/", SendSMSView.as_view(), name="sms-send"),
]
