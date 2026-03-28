from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "related_object_type",
            "related_object_id",
            "created_at",
            "time_ago",
        ]
        read_only_fields = fields

    def get_time_ago(self, obj):
        """Human-readable time since notification was created."""
        from django.utils import timezone

        now = timezone.now()
        diff = now - obj.created_at

        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days < 7:
            return f"{days}d ago"
        weeks = days // 7
        if weeks < 4:
            return f"{weeks}w ago"
        return obj.created_at.strftime("%b %d, %Y")
