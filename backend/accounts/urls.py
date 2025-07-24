from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("signin/", views.signin_view, name="signin"),
    path("signout/", views.signout_view, name="signout"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "verify-email/<str:token>/",
        views.verify_email_view,
        name="verify_email",
    ),
    path(
        "resend-verification/",
        views.resend_verification_view,
        name="resend_verification",
    ),
    path(
        "forgot-password/", views.forgot_password_view, name="forgot_password"
    ),
    path(
        "reset-password/<str:token>/",
        views.reset_password_view,
        name="reset_password",
    ),
]
