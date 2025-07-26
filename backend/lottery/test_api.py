from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from .models import DrawType, Draw, Prize, Ballot
from accounts.models import Account


class LotteryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            password="testpass123",
            last_name="User One",
        )
        self.user2 = User.objects.create_user(
            username="user2@example.com",
            email="user2@example.com",
            password="testpass123",
            last_name="User Two",
        )

        # Create accounts for users
        self.account1 = Account.objects.get(user=self.user1)
        self.account2 = Account.objects.get(user=self.user2)

        # Create draw type
        self.draw_type = DrawType.objects.create(
            name="Test Lottery", is_active=True, schedule={}
        )

        # Create prizes
        self.prize1 = Prize.objects.create(
            name="First Prize", amount=1000, number=1, drawtype=self.draw_type
        )
        self.prize2 = Prize.objects.create(
            name="Second Prize", amount=500, number=1, drawtype=self.draw_type
        )

        # Create draws
        self.open_draw = Draw.objects.create(
            drawtype=self.draw_type,
            date=date.today() + timedelta(days=7),
            closed=None,
        )

        self.closed_draw = Draw.objects.create(
            drawtype=self.draw_type,
            date=date.today() - timedelta(days=7),
            closed=timezone.now(),
        )

        # Create ballots
        self.ballot1 = Ballot.objects.create(
            account=self.account1, draw=self.open_draw
        )
        self.ballot2 = Ballot.objects.create(
            account=self.account1
        )  # Unassigned
        self.ballot3 = Ballot.objects.create(
            account=self.account2, draw=self.closed_draw, prize=self.prize1
        )

    def test_open_draws_api(self):
        """Test listing open draws"""
        url = reverse("lottery_api:open_draws")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.open_draw.id)
        self.assertIsNone(response.data[0]["closed"])

    def test_closed_draws_api(self):
        """Test listing closed draws"""
        url = reverse("lottery_api:closed_draws")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.closed_draw.id)
        self.assertIsNotNone(response.data[0]["closed"])
        self.assertIn("winners", response.data[0])

    def test_draw_detail_api(self):
        """Test getting draw details"""
        url = reverse(
            "lottery_api:draw_detail", kwargs={"pk": self.closed_draw.id}
        )
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.closed_draw.id)
        self.assertIn("winners", response.data)
        self.assertEqual(len(response.data["winners"]), 1)
        self.assertEqual(response.data["winners"][0]["name"], "User Two")

    def test_user_ballots_api_authenticated(self):
        """Test getting user ballots when authenticated"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lottery_api:user_ballots")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("unassigned_ballots", response.data)
        self.assertIn("assigned_ballots", response.data)
        self.assertIn("total_ballots", response.data)
        self.assertEqual(response.data["total_ballots"], 2)

    def test_user_ballots_api_unauthenticated(self):
        """Test getting user ballots when not authenticated"""
        url = reverse("lottery_api:user_ballots")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_purchase_ballots_api_success(self):
        """Test purchasing ballots successfully"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lottery_api:purchase_ballots")
        data = {
            "quantity": 3,
            "card_number": "4111111111111111",
            "expiry_month": 12,
            "expiry_year": 2025,
            "cvv": "123",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["ballots_created"], 3)

        # Check ballots were created
        self.assertEqual(
            Ballot.objects.filter(account__user=self.user1).count(), 5
        )  # 2 existing + 3 new

    def test_purchase_ballots_api_invalid_data(self):
        """Test purchasing ballots with invalid data"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lottery_api:purchase_ballots")
        data = {
            "quantity": 0,  # Invalid quantity
            "card_number": "invalid",
            "expiry_month": 13,  # Invalid month
            "expiry_year": 2025,
            "cvv": "12",  # Too short
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertIn("card_number", response.data)
        self.assertIn("expiry_month", response.data)
        self.assertIn("cvv", response.data)

    def test_assign_ballot_api_success(self):
        """Test assigning ballot to draw successfully"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:assign_ballot", kwargs={"ballot_id": self.ballot2.id}
        )
        data = {"draw_id": self.open_draw.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Check ballot was assigned
        self.ballot2.refresh_from_db()
        self.assertEqual(self.ballot2.draw, self.open_draw)

    def test_assign_ballot_api_already_assigned(self):
        """Test assigning already assigned ballot"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:assign_ballot", kwargs={"ballot_id": self.ballot1.id}
        )
        data = {"draw_id": self.open_draw.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_assign_ballot_api_closed_draw(self):
        """Test assigning ballot to closed draw"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:assign_ballot", kwargs={"ballot_id": self.ballot2.id}
        )
        data = {"draw_id": self.closed_draw.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("draw_id", response.data)

    def test_assign_ballot_api_wrong_user(self):
        """Test assigning ballot that doesn't belong to user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:assign_ballot", kwargs={"ballot_id": self.ballot3.id}
        )
        data = {"draw_id": self.open_draw.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ballot_detail_api_authenticated(self):
        """Test getting ballot details when authenticated"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:ballot_detail", kwargs={"pk": self.ballot1.id}
        )
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ballot1.id)

    def test_ballot_detail_api_wrong_user(self):
        """Test getting ballot details for another user's ballot"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            "lottery_api:ballot_detail", kwargs={"pk": self.ballot3.id}
        )
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_winnings_api(self):
        """Test getting user winnings"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("lottery_api:user_winnings")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_winnings", response.data)
        self.assertIn("total_winning_ballots", response.data)
        self.assertIn("winnings_by_draw", response.data)
        self.assertEqual(response.data["total_winnings"], 1000)
        self.assertEqual(response.data["total_winning_ballots"], 1)

    def test_user_winnings_api_no_winnings(self):
        """Test getting winnings for user with no wins"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("lottery_api:user_winnings")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_winnings"], 0)
        self.assertEqual(response.data["total_winning_ballots"], 0)

    def test_lottery_stats_api(self):
        """Test getting lottery statistics"""
        url = reverse("lottery_api:lottery_stats")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_draws", response.data)
        self.assertIn("open_draws", response.data)
        self.assertIn("closed_draws", response.data)
        self.assertIn("total_prizes_awarded", response.data)
        self.assertIn("total_amount_awarded", response.data)
        self.assertIn("recent_winners", response.data)
        self.assertEqual(response.data["total_draws"], 2)
        self.assertEqual(response.data["open_draws"], 1)
        self.assertEqual(response.data["closed_draws"], 1)
        self.assertEqual(response.data["total_prizes_awarded"], 1)
        self.assertEqual(response.data["total_amount_awarded"], 1000)

    def test_privacy_protection(self):
        """Test that user information is properly protected"""
        # Test that closed draws only show winner names, not other user info
        url = reverse("lottery_api:closed_draws")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        winner = response.data[0]["winners"][0]
        self.assertIn("name", winner)
        self.assertIn("prize_name", winner)
        self.assertIn("prize_amount", winner)
        # Should not contain email, user ID, or other sensitive info
        self.assertNotIn("email", winner)
        self.assertNotIn("user_id", winner)

    def test_ballot_ownership_protection(self):
        """Test that users can only access their own ballots"""
        self.client.force_authenticate(user=self.user1)

        # Try to access user2's ballot
        url = reverse(
            "lottery_api:ballot_detail", kwargs={"pk": self.ballot3.id}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to assign user2's ballot
        url = reverse(
            "lottery_api:assign_ballot", kwargs={"ballot_id": self.ballot3.id}
        )
        data = {"draw_id": self.open_draw.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
