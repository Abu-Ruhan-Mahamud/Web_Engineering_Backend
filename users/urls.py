from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("google-login/", views.google_login_view, name="google-login"),
    path("logout/", views.logout_view, name="logout"),
    path("delete-account/", views.delete_account_view, name="delete-account"),
    path("me/", views.me_view, name="me"),
    path("change-password/", views.change_password_view, name="change-password"),
    path("profile/", views.patient_profile_view, name="patient-profile"),
    path(
        "dashboard-stats/",
        views.patient_dashboard_stats,
        name="patient-dashboard-stats",
    ),
    path("doctors/", views.doctor_list_view, name="doctor-list"),
    # Doctor endpoints
    path(
        "doctor/dashboard-stats/",
        views.doctor_dashboard_stats,
        name="doctor-dashboard-stats",
    ),
    path("doctor/profile/", views.doctor_profile_view, name="doctor-profile"),
    path("doctor/schedule/", views.doctor_schedule_view, name="doctor-schedule"),
    path("doctor/patients/", views.doctor_patients_view, name="doctor-patients"),
    path(
        "doctor/patients/<int:patient_id>/",
        views.doctor_patient_detail_view,
        name="doctor-patient-detail",
    ),
]
