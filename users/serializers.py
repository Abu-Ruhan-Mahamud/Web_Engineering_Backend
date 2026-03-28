from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.conf import settings
from .models import User, Patient, Doctor


phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Phone number must be 7-15 digits, optionally starting with +.",
)


class AbsoluteImageURLField(serializers.ImageField):
    """Custom ImageField that returns absolute URLs."""
    
    def to_representation(self, value):
        """Return absolute URL for the image."""
        if not value:
            return None
        # Get the relative URL from the ImageField
        image_url = value.url
        # Get the request from context to build absolute URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(image_url)
        # Fallback to relative path
        return image_url


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for User model."""
    profile_picture = AbsoluteImageURLField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "profile_picture",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "email", "user_type", "is_active", "created_at"]
        extra_kwargs = {
            "phone": {"validators": [phone_validator]},
        }


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "date_of_birth",
            "gender",
            "blood_type",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "allergies",
            "chronic_conditions",
        ]


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Full read serializer — returns all fields (used for GET)."""

    class Meta:
        model = Doctor
        fields = [
            "license_number",
            "specialization",
            "years_experience",
            "bio",
            "consultation_fee",
            "available_days",
            "working_hours_start",
            "working_hours_end",
            "slot_duration",
        ]


class DoctorSelfUpdateSerializer(serializers.ModelSerializer):
    """Restricted write serializer — only fields a doctor may edit themselves.

    Credential fields (license_number, specialization, years_experience)
    are managed by admin/HR through the admin panel.
    """

    class Meta:
        model = Doctor
        fields = ["bio", "consultation_fee"]
        extra_kwargs = {
            "bio": {"required": False},
            "consultation_fee": {"required": False},
        }


class RegisterSerializer(serializers.Serializer):
    """Public registration — patients only.

    Doctors and admins are created by an admin from the admin panel.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(
        max_length=20, required=False, default="", validators=[phone_validator]
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")

        # Generate a username from email
        username = validated_data["email"].split("@")[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            password=password,
            user_type="patient",
            **validated_data,
        )

        # Create patient profile
        Patient.objects.create(user=user)

        return user


class DoctorListSerializer(serializers.ModelSerializer):
    """Read-only serializer for listing doctors (used in booking / search)."""

    id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
            "specialization",
            "years_experience",
            "bio",
            "consultation_fee",
            "available_days",
            "working_hours_start",
            "working_hours_end",
            "slot_duration",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email", "").lower()
        password = data.get("password")

        # Django's authenticate uses USERNAME_FIELD
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        data["user"] = user
        return data
