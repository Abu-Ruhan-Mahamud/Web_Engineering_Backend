from django.urls import path
from . import views

urlpatterns = [
    path("medications/", views.medication_list, name="medication-list"),
]
