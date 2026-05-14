from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from integrations.sms.models import SMSMessage
from integrations.sms.tasks import send_sms_task


class SendSMSView(APIView):
    def post(self, request):
        to = request.data.get("to")
        body = request.data.get("body")
        if not to or not body:
            return Response({"detail": "to and body are required"}, status=400)

        sms = SMSMessage.objects.create(to_number=to, body=body)
        send_sms_task.delay(str(sms.id))
        return Response({"id": str(sms.id), "status": sms.status}, status=status.HTTP_202_ACCEPTED)
