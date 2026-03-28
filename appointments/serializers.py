from rest_framework import serializers
from .models import Appointment
from users.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Full appointment serializer with nested doctor/patient info."""

    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "doctor_name",
            "doctor_specialization",
            "patient_name",
            "appointment_date",
            "appointment_time",
            "end_time",
            "status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"

    def get_doctor_specialization(self, obj):
        return obj.doctor.get_specialization_display()

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()


class CreateAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for booking a new appointment."""

    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "appointment_time", "reason"]

    def validate_appointment_date(self, value):
        from django.utils import timezone

        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Cannot book appointments in the past."
            )
        return value

    def validate(self, data):
        doctor = data["doctor"]
        appt_date = data["appointment_date"]
        appt_time = data["appointment_time"]

        # Check doctor is available on this day
        day_name = appt_date.strftime("%A").lower()
        if doctor.available_days and day_name not in [d.lower() for d in doctor.available_days]:
            raise serializers.ValidationError(
                {
                    "appointment_date": f"Dr. {doctor.user.get_full_name()} is not available on {day_name}s."
                }
            )

        # Check appointment time is within working hours
        if doctor.working_hours_start and appt_time < doctor.working_hours_start:
            raise serializers.ValidationError(
                {
                    "appointment_time": "Appointment time is before the doctor's working hours."
                }
            )
        if doctor.working_hours_end and appt_time >= doctor.working_hours_end:
            raise serializers.ValidationError(
                {
                    "appointment_time": "Appointment time is after the doctor's working hours."
                }
            )

        # Slot boundary enforcement
        if doctor.working_hours_start and doctor.slot_duration:
            start_minutes = doctor.working_hours_start.hour * 60 + doctor.working_hours_start.minute
            appt_minutes = appt_time.hour * 60 + appt_time.minute
            if (appt_minutes - start_minutes) % doctor.slot_duration != 0:
                raise serializers.ValidationError(
                    {
                        "appointment_time": f"Appointment time must align to {doctor.slot_duration}-minute slot boundaries starting from {doctor.working_hours_start.strftime('%I:%M %p')}."
                    }
                )

        # Check for double-booking (same doctor + date + time)
        if (
            Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appt_date,
                appointment_time=appt_time,
            )
            .exclude(status="cancelled")
            .exists()
        ):
            raise serializers.ValidationError(
                "This time slot is already booked for the selected doctor."
            )
        return data

    def create(self, validated_data):
        request = self.context["request"]
        patient = request.user.patient_profile
        # Calculate end_time based on doctor slot_duration
        doctor = validated_data["doctor"]
        from datetime import timedelta, datetime

        start = datetime.combine(
            validated_data["appointment_date"],
            validated_data["appointment_time"],
        )
        end = start + timedelta(minutes=doctor.slot_duration)
        validated_data["end_time"] = end.time()
        validated_data["patient"] = patient
        return super().create(validated_data)
