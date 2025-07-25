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
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from .forms import (
    UserSignUpForm,
    UserSignInForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
)
from .models import Account
from .tasks import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)


def signup_view(request):
    """Handle user signup."""
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verification
            user.save()

            # Send verification email
            send_verification_email.delay(user.email)
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
    """Handle user signin."""
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = UserSignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
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
    """Handle user signout."""
    logout(request)
    messages.success(request, "You have been signed out successfully.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


def verify_email_view(request, token):
    """Handle email verification."""
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
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html")


def resend_verification_view(request):
    """Handle resend verification email request."""
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            send_verification_email.delay(email)
            messages.success(
                request,
                "If an account exists with that email, a verification link "
                "has been sent.",
            )
        else:
            messages.error(request, "Please provide an email address.")

    return render(request, "accounts/resend_verification.html")


def forgot_password_view(request):
    """Handle password reset request."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            send_password_reset_email.delay(email)
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
    """Handle password reset."""
    try:
        account = Account.objects.get(
            password_reset_token=token,
            password_reset_expires__gt=timezone.now(),
        )

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
        messages.error(request, "Invalid or expired password reset link.")
        return redirect("accounts:forgot_password")
