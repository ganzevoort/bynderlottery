"""
Views for the accounts app.

- signup_view
- signin_view
- signout_view
- verify_email_view
- profile_view
- resend_verification_view
- forgot_password_view
- reset_password_view
"""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

from service.email import send_templated_email

from .forms import (
    UserSignUpForm,
    UserSignInForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
)
from .models import Account
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def send_verification_email(email):
    """Send verification email to user with given email."""
    try:
        user = User.objects.get(email=email)

        # Generate email verification token
        token = get_random_string(64)
        user.account.email_verification_token = token
        user.account.save()

        # Send verification email
        verification_url = reverse(
            "accounts:verify_email", kwargs={"token": token}
        )

        send_templated_email(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user.email,
            subject="Verify your email address",
            template_name="accounts/email/verify_email",
            context_dict={"verification_url": verification_url, "user": user},
        )
    except User.DoesNotExist:
        # User doesn't exist, but we don't want to reveal this
        pass
    except Exception as e:
        # Log the error but don't expose it to the user
        logger.error(f"Failed to send verification email to {email}: {e}")


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
        reset_url = reverse("accounts:reset_password", kwargs={"token": token})

        send_templated_email(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user.email,
            subject="Reset your password",
            template_name="accounts/email/password_reset",
            context_dict={"reset_url": reset_url, "user": user},
        )
    except User.DoesNotExist:
        # User doesn't exist, but we don't want to reveal this
        pass
    except Exception as e:
        # Log the error but don't expose it to the user
        logger.error(f"Failed to send password reset email to {email}: {e}")


def signup_view(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verification
            user.save()

            # Send verification email
            send_verification_email(user.email)
            messages.success(
                request,
                "Account created successfully! Please check your email to "
                "verify your account.",
            )
            return redirect("accounts:signin")
    else:
        form = UserSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def signin_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = UserSignInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(
                    request,
                    f"Welcome back, {user.last_name or user.email}!",
                )
                return redirect(settings.LOGIN_REDIRECT_URL)
        messages.error(
            request,
            "Invalid email or password. Maybe you need to verify your email?",
        )
    else:
        form = UserSignInForm()

    return render(request, "accounts/signin.html", {"form": form})


@login_required
def signout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


def verify_email_view(request, token):
    try:
        if not token:
            raise Account.DoesNotExist
        account = Account.objects.get(email_verification_token=token)
        account.user.is_active = True
        account.user.save()
        account.email_verified = True
        account.email_verification_token = ""
        account.save()
        messages.success(
            request,
            "Email verified successfully! You can now sign in.",
        )
        return redirect("accounts:signin")
    except Account.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect("accounts:signin")


@login_required
def profile_view(request):
    if request.method == "POST":
        bankaccount = request.POST.get("bankaccount", "")
        if len(bankaccount) <= 20:
            request.user.account.bankaccount = bankaccount
            request.user.account.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Bank account number is too long.")

    return render(request, "accounts/profile.html")


def resend_verification_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Account.objects.get(user__email=email).user
            if not user.is_active:
                # Send verification email
                send_verification_email(email)
                messages.success(
                    request,
                    "Verification email sent successfully!",
                )
            else:
                messages.info(request, "This account is already verified.")
        except Account.DoesNotExist:
            messages.error(
                request,
                "No account found with this email address.",
            )

    return render(request, "accounts/resend_verification.html")


def forgot_password_view(request):
    """Handle password reset request."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            send_password_reset_email(email)
            messages.success(
                request,
                "If an account with that email exists, a password reset link "
                "has been sent.",
            )
            return redirect("accounts:signin")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})


def reset_password_view(request, token):
    """Handle password reset with token."""
    try:
        account = Account.objects.get(password_reset_token=token)

        # Check if token is expired
        if (
            account.password_reset_expires
            and account.password_reset_expires < timezone.now()
        ):
            messages.error(
                request,
                "Password reset link has expired. Please request a new one.",
            )
            return redirect("accounts:forgot_password")

        if request.method == "POST":
            form = SetNewPasswordForm(account.user, request.POST)
            if form.is_valid():
                form.save()
                # Clear the reset token
                account.password_reset_token = ""
                account.password_reset_expires = None
                account.save()

                messages.success(
                    request,
                    "Your password has been reset successfully.",
                )
                return redirect("accounts:signin")
        else:
            form = SetNewPasswordForm(account.user)

        return render(request, "accounts/reset_password.html", {"form": form})

    except Account.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect("accounts:forgot_password")
