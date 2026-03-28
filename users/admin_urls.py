"""URL patterns for admin-only API endpoints.

Mounted at /api/admin/ in the root urlconf.
"""

from django.urls import path
from . import admin_views

urlpatterns = [
    path("stats/", admin_views.admin_stats_view, name="admin-stats"),
    path("users/", admin_views.admin_user_list_view, name="admin-user-list"),
    path(
        "users/<int:user_id>/",
        admin_views.admin_user_detail_view,
        name="admin-user-detail",
    ),
    path(
        "appointments/",
        admin_views.admin_appointment_list_view,
        name="admin-appointment-list",
    ),
    path(
        "appointments/export/",
        admin_views.admin_appointment_export_view,
        name="admin-appointment-export",
    ),
]
