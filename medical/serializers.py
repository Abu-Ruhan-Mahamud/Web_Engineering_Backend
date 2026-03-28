from rest_framework import serializers
from .models import MedicalRecord, Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "medication_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    prescriptions = PrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "appointment",
            "patient",
            "doctor",
            "doctor_name",
            "chief_complaint",
            "diagnosis",
            "symptoms",
            "examination_notes",
            "treatment_plan",
            "vitals",
            "additional_notes",
            "follow_up_date",
            "prescriptions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"


class CreateMedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for doctors to create a medical record with nested prescriptions."""

    prescriptions = PrescriptionSerializer(many=True, required=False, default=[])

    class Meta:
        model = MedicalRecord
        fields = [
            "appointment",
            "patient",
            "chief_complaint",
            "diagnosis",
            "symptoms",
            "examination_notes",
            "treatment_plan",
            "vitals",
            "additional_notes",
            "follow_up_date",
            "prescriptions",
        ]

    def validate(self, data):
        """Ensure doctor can only create records for their own patients."""
        from appointments.models import Appointment

        doctor = self.context["request"].user.doctor_profile
        patient = data.get("patient")
        appointment = data.get("appointment")

        # Verify doctor has appointment relationship with patient
        if patient and not Appointment.objects.filter(
            doctor=doctor, patient=patient
        ).exists():
            raise serializers.ValidationError(
                {"patient": "You have no appointments with this patient."}
            )

        # Verify appointment belongs to this doctor and patient
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
        prescriptions_data = validated_data.pop("prescriptions", [])
        doctor = self.context["request"].user.doctor_profile
        validated_data["doctor"] = doctor
        record = MedicalRecord.objects.create(**validated_data)
        for rx in prescriptions_data:
            Prescription.objects.create(medical_record=record, **rx)
        return record
