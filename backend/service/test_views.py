from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from lottery.models import DrawType, Prize, Draw, Ballot
from accounts.models import Account


@api_view(["POST"])
@permission_classes([AllowAny])
def clear_database(request):
    """Clear all test data from database"""
    try:
        # Clear all data
        Ballot.objects.all().delete()
        Draw.objects.all().delete()
        Prize.objects.all().delete()
        DrawType.objects.all().delete()
        Account.objects.all().delete()
        User.objects.all().delete()

        # Reset sequences
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")

        return Response(
            {"message": "Database cleared successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def seed_test_data(request):
    """Seed test data for Cypress tests"""
    try:
        call_command("seed_test_data")
        return Response(
            {"message": "Test data seeded successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_user(request):
    """Verify a user for testing purposes"""
    try:
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            account = Account.objects.get(user=user)

            # Activate user and verify email
            user.is_active = True
            user.save()

            account.email_verified = True
            account.save()

            return Response(
                {
                    "message": "User verified successfully",
                    "user_id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def test_health_check(request):
    """Health check endpoint for tests"""
    return Response(
        {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def get_test_tokens(request):
    """Get email verification and password reset tokens for testing purposes"""
    try:
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            account = user.account

            data = {
                "message": "Tokens retrieved successfully",
                "email": user.email,
                "email_verification_token": account.email_verification_token,
                "password_reset_token": account.password_reset_token,
                "password_reset_expires": (
                    account.password_reset_expires.isoformat()
                    if account.password_reset_expires
                    else None
                ),
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
