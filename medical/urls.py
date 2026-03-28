from django.urls import path
from . import views

urlpatterns = [
    path("records/", views.medical_record_list, name="medical-record-list"),
    path(
        "records/<int:pk>/", views.medical_record_detail, name="medical-record-detail"
    ),
    path("records/create/", views.create_medical_record, name="medical-record-create"),
]
