from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.messages import get_messages


class AccountViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password="testpass123",
            last_name="Active User",
        )
        self.active_account = self.active_user.account
        self.active_account.email_verified = True
        self.active_account.save()

        self.inactive_user = User.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password="testpass123",
            last_name="Inactive User",
            is_active=False,
        )
        self.inactive_account = self.inactive_user.account
        self.inactive_account.email_verification_token = "testtoken123"
        self.inactive_account.email_verified = False
        self.inactive_account.save()

    def test_signup_view_get(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_view_post_success(self):
        data = {
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
            "name": "New User",
        }
        response = self.client.post(reverse("accounts:signup"), data)
        self.assertRedirects(response, reverse("accounts:signin"))
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Account created successfully", str(messages[0]))

    def test_signin_view_success(self):
        data = {"username": "active@example.com", "password": "testpass123"}
        response = self.client.post(reverse("accounts:signin"), data)
        self.assertRedirects(response, reverse("index"))

    def test_signin_view_inactive_user(self):
        data = {"username": "inactive@example.com", "password": "testpass123"}
        response = self.client.post(reverse("accounts:signin"), data)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("verify your email", str(messages[0]))
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)

    def test_verify_email_view_success(self):
        response = self.client.get(
            reverse("accounts:verify_email", kwargs={"token": "testtoken123"})
        )
        self.assertRedirects(response, reverse("accounts:signin"))
        self.inactive_account.refresh_from_db()
        self.assertTrue(self.inactive_account.email_verified)
        self.assertEqual(self.inactive_account.email_verification_token, "")

    def test_verify_email_view_invalid_token(self):
        response = self.client.get(
            reverse("accounts:verify_email", kwargs={"token": "invalidtoken"})
        )
        self.assertRedirects(response, reverse("accounts:signin"))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Invalid verification link", str(messages[0]))

    def test_forgot_password_view(self):
        response = self.client.post(
            reverse("accounts:forgot_password"), {"email": "test@example.com"}
        )
        self.assertRedirects(response, reverse("accounts:signin"))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("If an account with that email exists", str(messages[0]))

    def test_reset_password_view_success(self):
        # Set up reset token
        self.active_account.password_reset_token = "resettoken123"
        self.active_account.password_reset_expires = (
            timezone.now() + timedelta(hours=23)
        )
        self.active_account.save()

        data = {
            "new_password1": "newpassword123",
            "new_password2": "newpassword123",
        }
        response = self.client.post(
            reverse(
                "accounts:reset_password", kwargs={"token": "resettoken123"}
            ),
            data,
        )
        self.assertRedirects(response, reverse("accounts:signin"))
        self.active_account.refresh_from_db()
        self.assertEqual(self.active_account.password_reset_token, "")
        self.assertIsNone(self.active_account.password_reset_expires)

    def test_reset_password_view_expired_token(self):
        self.active_account.password_reset_token = "resettoken123"
        self.active_account.password_reset_expires = (
            timezone.now() - timedelta(hours=1)
        )
        self.active_account.save()

        response = self.client.get(
            reverse(
                "accounts:reset_password", kwargs={"token": "resettoken123"}
            )
        )
        self.assertRedirects(response, reverse("accounts:forgot_password"))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Password reset link has expired", str(messages[0]))

    def test_profile_view_authenticated(self):
        self.client.force_login(self.active_user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_view_update_bankaccount(self):
        self.client.force_login(self.active_user)
        response = self.client.post(
            reverse("accounts:profile"), {"bankaccount": "123456789"}
        )
        self.assertEqual(response.status_code, 200)
        self.active_account.refresh_from_db()
        self.assertEqual(self.active_account.bankaccount, "123456789")
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Profile updated successfully", str(messages[0]))

    def test_signout_view(self):
        self.client.force_login(self.active_user)
        response = self.client.get(reverse("accounts:signout"))
        self.assertEqual(response.wsgi_request.user.is_authenticated, False)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "You have been successfully logged out", str(messages[0])
        )
