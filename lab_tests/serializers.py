from rest_framework import serializers
from .models import LabTest, LabTestResult


class LabTestResultSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    test_category = serializers.CharField(source="lab_test.test_category", read_only=True)

    class Meta:
        model = LabTestResult
        fields = [
            "id",
            "test_category",
            "result_value",
            "reference_range",
            "unit",
            "findings",
            "impression",
            "interpretation",
            "result_file",
            "notes",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
        ]
        read_only_fields = ["id", "test_category", "uploaded_by", "uploaded_by_name", "uploaded_at"]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name()
        return None


class LabTestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    result = LabTestResultSerializer(read_only=True)

    class Meta:
        model = LabTest
        fields = [
            "id",
            "patient",
            "doctor",
            "doctor_name",
            "patient_name",
            "appointment",
            "test_name",
            "test_category",
            "priority",
            "status",
            "clinical_notes",
            "ordered_at",
            "completed_at",
            "reviewed_at",
            "reviewed_by",
            "result",
        ]
        read_only_fields = [
            "id",
            "ordered_at",
            "completed_at",
            "reviewed_at",
            "reviewed_by",
        ]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()


class CreateLabTestSerializer(serializers.ModelSerializer):
    """Serializer for doctors to order a lab test."""

    class Meta:
        model = LabTest
        fields = [
            "patient",
            "appointment",
            "test_name",
            "test_category",
            "priority",
            "clinical_notes",
        ]

    def validate(self, data):
        from appointments.models import Appointment

        doctor = self.context["request"].user.doctor_profile
        patient = data.get("patient")
        appointment = data.get("appointment")

        # Verify doctor has treated this patient
        if patient and not Appointment.objects.filter(
            doctor=doctor, patient=patient
        ).exists():
            raise serializers.ValidationError(
                {"patient": "You have no appointments with this patient."}
            )

        if appointment:
            if appointment.doctor_id != doctor.pk:
                raise serializers.ValidationError(
                    {"appointment": "This appointment does not belong to you."}
                )
            if patient and appointment.patient_id != patient.pk:
                raise serializers.ValidationError(
                    {
                        "appointment": "This appointment does not match the specified patient."
                    }
                )

        return data

    def create(self, validated_data):
        doctor = self.context["request"].user.doctor_profile
        validated_data["doctor"] = doctor
        return LabTest.objects.create(**validated_data)


class UploadLabResultSerializer(serializers.ModelSerializer):
    """Serializer for lab techs to upload results."""

    class Meta:
        model = LabTestResult
        fields = [
            "result_value",
            "reference_range",
            "unit",
            "findings",
            "impression",
            "interpretation",
            "result_file",
            "notes",
        ]
