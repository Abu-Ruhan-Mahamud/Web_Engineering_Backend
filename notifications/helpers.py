"""
Notification creation helper.

Import and call from any view that needs to generate notifications:

    from notifications.helpers import create_notification

    create_notification(
        recipient=some_user,
        title="Appointment Confirmed",
        message="Your appointment with Dr. Smith on Feb 10 has been confirmed.",
        notification_type="appointment",
        related_object_type="appointment",
        related_object_id=appointment.id,
    )
"""

from .models import Notification


def create_notification(
    recipient,
    title,
    message,
    notification_type="system",
    related_object_type="",
    related_object_id=None,
):
    """
    Create a single notification for a user.
    Returns the created Notification instance.
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )


def create_bulk_notifications(recipients, title, message, notification_type="system",
                              related_object_type="", related_object_id=None):
    """
    Create the same notification for multiple users at once.
    Uses bulk_create for efficiency.
    Returns the list of created Notification instances.
    """
    notifications = [
        Notification(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )
        for user in recipients
    ]
    return Notification.objects.bulk_create(notifications)
