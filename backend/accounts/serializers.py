from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Account


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    email = serializers.EmailField()
    name = serializers.CharField(source="last_name", max_length=150)

    class Meta:
        model = User
        fields = ["id", "email", "name", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ["id", "user", "bankaccount", "email_verified", "created_at"]
        read_only_fields = ["id", "user", "email_verified", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (combines User and Account data)"""

    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.CharField(source="user.last_name", max_length=150)
    bankaccount = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    email_verified = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(
        source="user.date_joined", read_only=True
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "name",
            "bankaccount",
            "email_verified",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "email_verified", "date_joined"]

    def update(self, instance, validated_data):
        # Update user name if provided
        if "user" in validated_data and "last_name" in validated_data["user"]:
            instance.user.last_name = validated_data["user"]["last_name"]
            instance.user.save()

        # Update account bankaccount if provided
        if "bankaccount" in validated_data:
            instance.bankaccount = validated_data["bankaccount"]

        instance.save()
        return instance


class SignUpSerializer(serializers.Serializer):
    """Serializer for user signup"""

    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=150)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists"
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password1"],
            last_name=validated_data["name"],
            is_active=False,  # Will be activated after email verification
        )
        return user


class SignInSerializer(serializers.Serializer):
    """Serializer for user signin"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError(
                    "Account is not active. Please verify your email first."
                )
            attrs["user"] = user
        else:
            raise serializers.ValidationError(
                "Must include email and password"
            )

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password"""

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists or not for security
            pass
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""

    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer for profile updates"""

    name = serializers.CharField(max_length=150, required=False)
    bankaccount = serializers.CharField(max_length=20, required=False)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            instance.user.last_name = validated_data["name"]
            instance.user.save()

        if "bankaccount" in validated_data:
            instance.bankaccount = validated_data["bankaccount"]
            instance.save()

        return instance
