from django.urls import path
from integrations.crm.views import CRMContactListView, CRMSyncView

urlpatterns = [
    path("contacts/", CRMContactListView.as_view(), name="crm-contacts"),
    path("sync/", CRMSyncView.as_view(), name="crm-sync"),
]
