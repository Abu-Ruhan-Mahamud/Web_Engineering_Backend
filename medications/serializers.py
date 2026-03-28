from rest_framework import serializers
from .models import Medication


class MedicationSerializer(serializers.ModelSerializer):
    prescribed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Medication
        fields = [
            "id",
            "name",
            "dosage",
            "frequency",
            "start_date",
            "end_date",
            "is_active",
            "prescribed_by",
            "prescribed_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_prescribed_by_name(self, obj):
        if obj.prescribed_by:
            return f"Dr. {obj.prescribed_by.user.get_full_name()}"
        return None
