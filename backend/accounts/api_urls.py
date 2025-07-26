from django.urls import path
from . import api_views

app_name = "accounts_api"

urlpatterns = [
    # Authentication endpoints
    path("signup/", api_views.SignUpView.as_view(), name="signup"),
    path("signin/", api_views.SignInView.as_view(), name="signin"),
    path("signout/", api_views.SignOutView.as_view(), name="signout"),
    # Email verification endpoints
    path(
        "verify-email/<str:token>/",
        api_views.VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path(
        "resend-verification/",
        api_views.ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    # Password reset endpoints
    path(
        "forgot-password/",
        api_views.ForgotPasswordView.as_view(),
        name="forgot_password",
    ),
    path(
        "reset-password/<str:token>/",
        api_views.ResetPasswordView.as_view(),
        name="reset_password",
    ),
    # Profile endpoint
    path("profile/", api_views.ProfileView.as_view(), name="profile"),
]
