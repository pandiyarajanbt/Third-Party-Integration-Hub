from rest_framework.response import Response
from rest_framework.views import APIView
from integrations.crm.models import CRMContact
from integrations.crm.tasks import sync_crm_contacts


class CRMContactListView(APIView):
    def get(self, request):
        contacts = CRMContact.objects.values(
            "id", "crm_id", "email", "first_name", "last_name", "synced_at"
        ).order_by("-synced_at")[:100]
        return Response(list(contacts))


class CRMSyncView(APIView):
    def post(self, request):
        task = sync_crm_contacts.delay()
        return Response({"task_id": task.id, "status": "sync started"}, status=202)
