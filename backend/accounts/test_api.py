from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from .models import Account


class AccountsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
            last_name="Test User",
        )
        self.account = Account.objects.get(user=self.user)

    @patch("accounts.tasks.send_verification_email.delay")
    def test_signup_api(self, mock_send_email):
        """Test user signup via API"""
        url = reverse("accounts_api:signup")
        data = {
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
            "name": "New User",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

        # Check user was created
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.last_name, "New User")
        self.assertFalse(
            user.is_active
        )  # Should be inactive until email verification

        # Check verification email was sent
        mock_send_email.assert_called_once_with("new@example.com")

    def test_signup_api_password_mismatch(self):
        """Test signup with mismatched passwords"""
        url = reverse("accounts_api:signup")
        data = {
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "differentpass",
            "name": "New User",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_signup_api_duplicate_email(self):
        """Test signup with existing email"""
        url = reverse("accounts_api:signup")
        data = {
            "email": "test@example.com",  # Already exists
            "password1": "newpass123",
            "password2": "newpass123",
            "name": "New User",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_signin_api_success(self):
        """Test successful signin via API"""
        # Activate the user first
        self.user.is_active = True
        self.user.save()

        url = reverse("accounts_api:signin")
        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_signin_api_invalid_credentials(self):
        """Test signin with invalid credentials"""
        url = reverse("accounts_api:signin")
        data = {"email": "test@example.com", "password": "wrongpassword"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_signin_api_inactive_user(self):
        """Test signin with inactive user"""
        # Ensure user is inactive
        self.user.is_active = False
        self.user.save()

        url = reverse("accounts_api:signin")
        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_signout_api(self):
        """Test signout via API"""
        # First sign in
        self.client.force_authenticate(user=self.user)

        url = reverse("accounts_api:signout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_profile_api_get(self):
        """Test getting user profile via API"""
        self.client.force_authenticate(user=self.user)

        url = reverse("accounts_api:profile")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["name"], "Test User")

    def test_profile_api_update(self):
        """Test updating user profile via API"""
        self.client.force_authenticate(user=self.user)

        url = reverse("accounts_api:profile")
        data = {"name": "Updated Name", "bankaccount": "NL91ABNA0417164300"}

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check updates
        self.user.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(self.user.last_name, "Updated Name")
        self.assertEqual(self.account.bankaccount, "NL91ABNA0417164300")

    def test_profile_api_unauthorized(self):
        """Test profile access without authentication"""
        url = reverse("accounts_api:profile")
        response = self.client.get(url, format="json")
        # DRF returns 403 for permission denied, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("accounts.tasks.send_verification_email.delay")
    def test_resend_verification_api(self, mock_send_email):
        """Test resending verification email via API"""
        # Make sure user is inactive
        self.user.is_active = False
        self.user.save()

        url = reverse("accounts_api:resend_verification")
        data = {"email": "test@example.com"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_send_email.assert_called_once_with("test@example.com")

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_forgot_password_api(self, mock_send_email):
        """Test forgot password via API"""
        url = reverse("accounts_api:forgot_password")
        data = {"email": "test@example.com"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_send_email.assert_called_once_with("test@example.com")

    def test_verify_email_api_success(self):
        """Test email verification via API"""
        # Set up verification token
        self.account.email_verification_token = "test-token"
        self.account.save()

        url = reverse(
            "accounts_api:verify_email", kwargs={"token": "test-token"}
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Check user is now active
        self.user.refresh_from_db()
        self.account.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.account.email_verified)

    def test_verify_email_api_invalid_token(self):
        """Test email verification with invalid token"""
        url = reverse(
            "accounts_api:verify_email", kwargs={"token": "invalid-token"}
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
