"""
Tasks for the accounts app.

- send_verification_email
- send_password_reset_email
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.models import User

from service.background import celery_app
from service.email import send_templated_email


logger = logging.getLogger(__name__)


@celery_app.task(ignore_result=True)
def send_verification_email(email):
    """Send verification email to user with given email."""
    try:
        user = User.objects.get(email=email)

        # Generate email verification token
        token = get_random_string(64)
        user.account.email_verification_token = token
        user.account.save()

        # Send verification email
        verification_url = f"/auth/verify-email/{token}/"
        send_templated_email(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user.email,
            subject="Verify your email address",
            template_name="accounts/email/verify_email",
            context_dict={"verification_url": verification_url, "user": user},
        )
        logger.info(f"Verification email sent to {email}")
    except User.DoesNotExist:
        logger.error(f"Verification email request for nonexistent {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")


@celery_app.task(ignore_result=True)
def send_password_reset_email(email):
    """Send password reset email to user with given email."""
    try:
        user = User.objects.get(email=email)
        account = user.account

        # Generate password reset token
        token = get_random_string(64)
        account.password_reset_token = token
        account.password_reset_expires = timezone.now() + timedelta(hours=24)
        account.save()

        # Send password reset email
        reset_url = f"/auth/reset-password/{token}/"
        send_templated_email(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user.email,
            subject="Reset your password",
            template_name="accounts/email/password_reset",
            context_dict={"reset_url": reset_url, "user": user},
        )
        logger.info(f"Password reset email sent to {email}")
    except User.DoesNotExist:
        logger.error(f"Password reset request for nonexistent {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
