from django.urls import path
from . import views

urlpatterns = [
    path("notifications/", views.notification_list, name="notification-list"),
    path("notifications/<int:pk>/read/", views.notification_read, name="notification-read"),
    path("notifications/<int:pk>/delete/", views.notification_delete, name="notification-delete"),
    path("notifications/mark-all-read/", views.mark_all_read, name="notification-mark-all-read"),
    path("notifications/unread-count/", views.unread_count, name="notification-unread-count"),
    path("notifications/clear/", views.clear_all_notifications, name="notification-clear"),
]
