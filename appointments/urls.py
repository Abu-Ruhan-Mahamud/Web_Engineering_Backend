from django.urls import path
from . import views

urlpatterns = [
    path("appointments/", views.appointment_list, name="appointment-list"),
    path("appointments/booked-slots/", views.booked_slots, name="booked-slots"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment-detail"),
]
