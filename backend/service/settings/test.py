"""
Test settings for Lottery System
"""

SECRET_KEY = "test-secret-key-for-testing-only"
TIME_ZONE = "Europe/Amsterdam"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ["web", "localhost"]

# Celery - Always eager for testing (no background tasks)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
REDIS_HOST = "localhost"
REDIS_PORT = 6379
