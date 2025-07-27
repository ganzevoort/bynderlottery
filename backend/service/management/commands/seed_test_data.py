from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from lottery.models import DrawType, Prize, Draw, Ballot
from accounts.models import Account


class Command(BaseCommand):
    help = "Seed test data for Cypress integration tests"

    def handle(self, *args, **options):
        self.stdout.write("Seeding test data...")

        # Create test draw types
        daily_draw, created = DrawType.objects.get_or_create(
            name="Daily Draw",
            defaults={
                "is_active": True,
                "schedule": {"frequency": "daily", "time": "20:00"},
            },
        )
        if created:
            self.stdout.write(f"Created draw type: {daily_draw.name}")

        weekly_draw, created = DrawType.objects.get_or_create(
            name="Weekly Draw",
            defaults={
                "is_active": True,
                "schedule": {
                    "frequency": "weekly",
                    "day": "saturday",
                    "time": "19:00",
                },
            },
        )
        if created:
            self.stdout.write(f"Created draw type: {weekly_draw.name}")

        # Create prizes for daily draw
        daily_prizes = [
            {"name": "First Prize", "amount": 1000, "number": 1},
            {"name": "Second Prize", "amount": 500, "number": 2},
            {"name": "Third Prize", "amount": 250, "number": 3},
        ]

        for prize_data in daily_prizes:
            prize, created = Prize.objects.get_or_create(
                name=prize_data["name"],
                drawtype=daily_draw,
                defaults={
                    "amount": prize_data["amount"],
                    "number": prize_data["number"],
                },
            )
            if created:
                self.stdout.write(f"Created prize: {prize.name}")

        # Create prizes for weekly draw
        weekly_prizes = [
            {"name": "Jackpot", "amount": 5000, "number": 1},
            {"name": "Runner Up", "amount": 1000, "number": 2},
            {"name": "Consolation", "amount": 100, "number": 5},
        ]

        for prize_data in weekly_prizes:
            prize, created = Prize.objects.get_or_create(
                name=prize_data["name"],
                drawtype=weekly_draw,
                defaults={
                    "amount": prize_data["amount"],
                    "number": prize_data["number"],
                },
            )
            if created:
                self.stdout.write(f"Created prize: {prize.name}")

        # Create open draws (future dates)
        tomorrow = timezone.now() + timedelta(days=1)
        next_week = timezone.now() + timedelta(days=7)

        daily_draw_open, created = Draw.objects.get_or_create(
            drawtype=daily_draw, date=tomorrow, defaults={"closed": None}
        )
        if created:
            self.stdout.write(f"Created open daily draw for {tomorrow.date()}")

        weekly_draw_open, created = Draw.objects.get_or_create(
            drawtype=weekly_draw, date=next_week, defaults={"closed": None}
        )
        if created:
            self.stdout.write(
                f"Created open weekly draw for {next_week.date()}"
            )

        # Create closed draws (past dates) with winners
        yesterday = timezone.now() - timedelta(days=1)
        last_week = timezone.now() - timedelta(days=7)

        daily_draw_closed, created = Draw.objects.get_or_create(
            drawtype=daily_draw,
            date=yesterday,
            defaults={"closed": yesterday + timedelta(hours=1)},
        )
        if created:
            self.stdout.write(
                f"Created closed daily draw for {yesterday.date()}"
            )

        weekly_draw_closed, created = Draw.objects.get_or_create(
            drawtype=weekly_draw,
            date=last_week,
            defaults={"closed": last_week + timedelta(hours=1)},
        )
        if created:
            self.stdout.write(
                f"Created closed weekly draw for {last_week.date()}"
            )

        # Create test users with accounts
        test_users = [
            {
                "email": "testuser1@example.com",
                "first_name": "Test",
                "last_name": "User 1",
                "password": "testpass123",
            },
            {
                "email": "testuser2@example.com",
                "first_name": "Test",
                "last_name": "User 2",
                "password": "testpass123",
            },
            {
                "email": "winner@example.com",
                "first_name": "Lucky",
                "last_name": "Winner",
                "password": "testpass123",
            },
        ]

        for user_data in test_users:
            user = User.objects.create(
                username=user_data["email"],  # Use email as username
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=True,
            )
            user.set_password(user_data["password"])
            user.save()
            self.stdout.write(f"Created user: {user.username}")

            # Ensure account is properly configured
            user.account.email_verified = True
            user.account.bankaccount = "NL91ABNA0417164300"
            user.account.save()
            self.stdout.write(f"Configured account for user: {user.username}")

        # Create some test ballots
        winner_user = User.objects.get(username="winner@example.com")
        winner_account = Account.objects.get(user=winner_user)

        # Create assigned ballots for closed draws
        for i in range(3):
            ballot = Ballot.objects.create(
                account=winner_account, draw=daily_draw_closed, prize=None
            )
            self.stdout.write(
                f"Created assigned ballot {ballot.id} for closed draw"
            )

        # Create unassigned ballots for test user
        test_user = User.objects.get(username="testuser1@example.com")
        test_account = Account.objects.get(user=test_user)

        for i in range(5):
            ballot = Ballot.objects.create(
                account=test_account, draw=None, prize=None
            )
            self.stdout.write(
                f"Created unassigned ballot {ballot.id} for test user"
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded test data!"))
