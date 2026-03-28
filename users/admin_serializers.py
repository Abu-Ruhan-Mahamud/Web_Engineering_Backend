"""Serializers for admin-only endpoints."""

from rest_framework import serializers
from .models import User, Patient, Doctor


class AdminUserListSerializer(serializers.ModelSerializer):
    """Compact user serializer for the admin user list table."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "phone",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer (view / edit single user)."""

    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "phone",
            "profile_picture",
            "is_active",
            "created_at",
            "updated_at",
            "profile",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "profile"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_profile(self, obj):
        if obj.user_type == "patient" and hasattr(obj, "patient_profile"):
            p = obj.patient_profile
            return {
                "date_of_birth": p.date_of_birth,
                "gender": p.gender,
                "blood_type": p.blood_type,
                "address": p.address,
                "emergency_contact_name": p.emergency_contact_name,
                "emergency_contact_phone": p.emergency_contact_phone,
            }
        if obj.user_type == "doctor" and hasattr(obj, "doctor_profile"):
            d = obj.doctor_profile
            return {
                "license_number": d.license_number,
                "specialization": d.get_specialization_display(),
                "specialization_key": d.specialization,
                "years_experience": d.years_experience,
                "bio": d.bio,
                "consultation_fee": str(d.consultation_fee),
            }
        return None


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin editing a user (toggle active, update info)."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "is_active",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
            "is_active": {"required": False},
        }


class AdminDoctorCreateSerializer(serializers.Serializer):
    """Admin-only: create a new doctor or admin account."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, default="")
    user_type = serializers.ChoiceField(choices=["doctor", "admin", "lab_tech"])

    # Doctor-specific (required when user_type == doctor)
    license_number = serializers.CharField(max_length=50, required=False, default="")
    specialization = serializers.CharField(max_length=50, required=False, default="")
    years_experience = serializers.IntegerField(required=False, default=0)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data["user_type"] == "doctor":
            if not data.get("license_number"):
                raise serializers.ValidationError(
                    {"license_number": "Required for doctor accounts."}
                )
            if not data.get("specialization"):
                raise serializers.ValidationError(
                    {"specialization": "Required for doctor accounts."}
                )
        return data

    def create(self, validated_data):
        license_number = validated_data.pop("license_number", "")
        specialization = validated_data.pop("specialization", "")
        years_experience = validated_data.pop("years_experience", 0)
        password = validated_data.pop("password")
        user_type = validated_data.pop("user_type")

        # Generate unique username
        username = validated_data["email"].split("@")[0]
        base = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            password=password,
            user_type=user_type,
            **validated_data,
        )

        if user_type == "doctor":
            Doctor.objects.create(
                user=user,
                license_number=license_number,
                specialization=specialization,
                years_experience=years_experience,
            )
        elif user_type == "admin":
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        # lab_tech needs no extra profile — just the User record

        return user
