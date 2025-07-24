"""
Make sure a superuser exists.

If not, create superuser admin with password as specified in
settings (from environment).
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            return
        elif settings.ADMIN_PASSWORD:
            User.objects.create_superuser(
                settings.ADMIN_EMAIL,
                settings.ADMIN_EMAIL,
                settings.ADMIN_PASSWORD,
                last_name="Lottery Admin",
            )
            print("Created default admin.")
        else:
            raise CommandError("Set ADMIN_PASSWORD in the environment")
