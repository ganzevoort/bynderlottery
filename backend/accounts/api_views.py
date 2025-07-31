from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Account
from .serializers import (
    SignUpSerializer,
    SignInSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ProfileSerializer,
)
from .tasks import send_verification_email, send_password_reset_email


@extend_schema(
    tags=["Authentication"],
    summary="User Registration",
    description="Register a new user account",
    request=SignUpSerializer,
    responses={
        201: {
            "description": "User created successfully",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": (
                        "Account created successfully. "
                        "Please check your email to verify your account."
                    ),
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Email already exists"}
            },
        },
    },
)
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
                    )
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="User Login",
    description="Authenticate and login a user",
    request=SignInSerializer,
    responses={
        200: {
            "description": "Login successful",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Successfully signed in!",
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid credentials"}
            },
        },
    },
)
class SignInView(APIView):
    """API endpoint for user signin"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            if user and user.is_active:
                login(request, user)
                return Response(
                    {"message": "Successfully signed in!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    summary="User Logout",
    description="Logout the current user",
    responses={
        200: {
            "description": "Logout successful",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Successfully signed out!",
                }
            },
        }
    },
)
class SignOutView(APIView):
    """API endpoint for user signout"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Successfully signed out!"},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Email Verification",
    description="Verify user email with token",
    parameters=[
        OpenApiParameter(
            name="token",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Email verification token",
            examples=[
                OpenApiExample(
                    "Verification Token",
                    value="abc123def456",
                    description="Email verification token",
                )
            ],
        )
    ],
    responses={
        200: {
            "description": "Email verified successfully",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": (
                        "Email verified successfully. You can now sign in."
                    ),
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Invalid verification link.",
                }
            },
        },
    },
)
class VerifyEmailView(APIView):
    """API endpoint for email verification"""

    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            account = Account.objects.get(
                email_verification_token=token, email_verified=False
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
                        "Email verified successfully. You can now sign in."
                    )
                },
                status=status.HTTP_200_OK,
            )

        except Account.DoesNotExist:
            return Response(
                {"error": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    tags=["Authentication"],
    summary="Resend Verification Email",
    description="Request a new verification email to be sent",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email",
                    "example": "user@example.com",
                }
            },
            "required": ["email"],
        }
    },
    responses={
        200: {
            "description": "Verification email sent",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": (
                        "If an account with that email exists, "
                        "a verification email has been sent."
                    ),
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Email is required"}
            },
        },
    },
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


@extend_schema(
    tags=["Authentication"],
    summary="Forgot Password",
    description="Request a password reset email",
    request=ForgotPasswordSerializer,
    responses={
        200: {
            "description": "Password reset email sent",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": (
                        "If an account with that email exists, "
                        "a password reset email has been sent."
                    ),
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Email is required"}
            },
        },
    },
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


@extend_schema(
    tags=["Authentication"],
    summary="Reset Password",
    description="Reset password using token",
    parameters=[
        OpenApiParameter(
            name="token",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Password reset token",
            examples=[
                OpenApiExample(
                    "Reset Token",
                    value="abc123def456",
                    description="Password reset token",
                )
            ],
        )
    ],
    request=ResetPasswordSerializer,
    responses={
        200: {
            "description": "Password reset successful",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Password reset successfully.",
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid reset token."}
            },
        },
    },
)
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
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )

            except Account.DoesNotExist:
                return Response(
                    {"error": "Invalid reset token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["User Profile"],
    summary="Get User Profile",
    description="Get the current user's profile information",
    responses={
        200: ProfileSerializer,
        401: {
            "description": "Unauthorized",
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
)
class ProfileView(APIView):
    """API endpoint for user profile"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user.account)
        return Response(serializer.data)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: {
                "description": "Bad request",
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Invalid data"}
                },
            },
        },
    )
    def put(self, request):
        serializer = ProfileSerializer(
            request.user.account, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
