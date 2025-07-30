from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .serializers import (
    SignUpSerializer,
    SignInSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ProfileUpdateSerializer,
    AccountSerializer,
)
from .models import Account
from .tasks import send_verification_email, send_password_reset_email


class SignUpView(APIView):
    """API endpoint for user signup"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send verification email
            try:
                send_verification_email.delay(user.email)
            except Exception:
                # Log error but don't expose to user
                pass

            return Response(
                {
                    "message": (
                        "Account created successfully. "
                        "Please check your email to verify your account."
                    ),
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    """API endpoint for user signin"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)

            return Response(
                {
                    "message": "Successfully signed in",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.last_name,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignOutView(APIView):
    """API endpoint for user signout"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Successfully signed out"}, status=status.HTTP_200_OK
        )


class VerifyEmailView(APIView):
    """API endpoint for email verification"""

    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            account = Account.objects.get(
                email_verification_token=token, email_verified=False
            )

            # Check if token is expired (24 hours)
            if account.created_at < timezone.now() - timedelta(hours=24):
                return Response(
                    {
                        "error": (
                            "Verification link has expired. "
                            "Please request a new one."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify email
            account.email_verified = True
            account.email_verification_token = ""
            account.save()

            # Activate user
            user = account.user
            user.is_active = True
            user.save()

            return Response(
                {
                    "message": (
                        "Email verified successfully. " "You can now sign in."
                    )
                },
                status=status.HTTP_200_OK,
            )

        except Account.DoesNotExist:
            return Response(
                {"error": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendVerificationView(APIView):
    """API endpoint for resending verification email"""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            if user.account.email_verified:
                return Response(
                    {"error": "Account is already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send verification email
            try:
                send_verification_email.delay(user.email)
            except Exception:
                # Log error but don't expose to user
                pass

            return Response(
                {
                    "message": (
                        "If an account with that email exists, "
                        "a verification email has been sent."
                    )
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # Don't reveal if user exists or not
            return Response(
                {
                    "message": (
                        "If an account with that email exists, "
                        "a verification email has been sent."
                    )
                },
                status=status.HTTP_200_OK,
            )


class ForgotPasswordView(APIView):
    """API endpoint for forgot password"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Send password reset email
            try:
                send_password_reset_email.delay(email)
            except Exception:
                # Log error but don't expose to user
                pass

            return Response(
                {
                    "message": (
                        "If an account with that email exists, "
                        "a password reset email has been sent."
                    )
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """API endpoint for password reset"""

    permission_classes = [AllowAny]

    def post(self, request, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                account = Account.objects.get(
                    password_reset_token=token,
                    password_reset_expires__gt=timezone.now(),
                )

                # Reset password
                user = account.user
                user.set_password(serializer.validated_data["password1"])
                user.save()

                # Clear reset token
                account.password_reset_token = ""
                account.password_reset_expires = None
                account.save()

                return Response(
                    {
                        "message": (
                            "Password reset successfully. "
                            "You can now sign in with your new password."
                        )
                    },
                    status=status.HTTP_200_OK,
                )

            except Account.DoesNotExist:
                return Response(
                    {"error": "Invalid or expired reset link."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """API endpoint for user profile"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user's profile"""
        account = get_object_or_404(Account, user=request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def put(self, request):
        """Update current user's profile"""
        account = get_object_or_404(Account, user=request.user)
        serializer = ProfileUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.update(account, serializer.validated_data)
            # Return updated profile
            account_serializer = AccountSerializer(account)
            return Response(account_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
