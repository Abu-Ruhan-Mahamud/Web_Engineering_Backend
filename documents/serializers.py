from rest_framework import serializers
from .models import MedicalDocument


class MedicalDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    document_type_display = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalDocument
        fields = [
            "id",
            "patient",
            "file",
            "file_url",
            "document_type",
            "document_type_display",
            "title",
            "description",
            "file_size",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "file_size", "uploaded_by", "created_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_document_type_display(self, obj):
        return obj.get_document_type_display()

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return "Unknown"


class UploadDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDocument
        fields = ["file", "document_type", "title", "description"]

    def validate_file(self, value):
        max_size = 10 * 1024 * 1024  # 10 MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size ({value.size // (1024*1024)}MB) exceeds the 10MB limit."
            )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["patient"] = request.user.patient_profile
        validated_data["uploaded_by"] = request.user
        if validated_data.get("file"):
            validated_data["file_size"] = validated_data["file"].size
        return super().create(validated_data)
