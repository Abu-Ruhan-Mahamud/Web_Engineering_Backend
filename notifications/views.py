from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer
from curova_backend.pagination import paginate_queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    GET /api/notifications/
    List all notifications for the authenticated user.
    Supports filtering: ?is_read=true/false, ?type=appointment
    """
    queryset = Notification.objects.filter(recipient=request.user)

    # Optional filters
    is_read = request.query_params.get("is_read")
    if is_read is not None:
        queryset = queryset.filter(is_read=is_read.lower() == "true")

    notification_type = request.query_params.get("type")
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)

    return paginate_queryset(queryset, request, NotificationSerializer)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def notification_read(request, pk):
    """
    PATCH /api/notifications/<id>/read/
    Mark a single notification as read.
    """
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return Response(
            {"error": "Notification not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return Response(NotificationSerializer(notification).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """
    POST /api/notifications/mark-all-read/
    Mark all unread notifications as read for the authenticated user.
    """
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)

    return Response({"marked_read": count})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """
    GET /api/notifications/unread-count/
    Returns the count of unread notifications. Lightweight endpoint for badge polling.
    Also lazily generates medication reminder notifications for patients.
    """
    # Auto-generate any due medication reminders (idempotent)
    from medications.reminders import check_medication_reminders

    check_medication_reminders(request.user)

    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    return Response({"unread_count": count})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def notification_delete(request, pk):
    """
    DELETE /api/notifications/<id>/
    Delete a single notification.
    """
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return Response(
            {"error": "Notification not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    notification.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_all_notifications(request):
    """
    DELETE /api/notifications/clear/
    Delete all notifications for the authenticated user.
    """
    count = Notification.objects.filter(recipient=request.user).delete()[0]
    return Response({"deleted": count})
