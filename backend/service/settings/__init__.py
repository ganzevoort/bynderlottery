import os
from importlib import import_module

from .defaults import *
from .environment import *


# Load layer settings
try:
    m = import_module(f"service.settings.{os.getenv('LAYER', 'dev')}")
    globals().update(m.__dict__)
except ModuleNotFoundError:
    pass


# Test-specific settings
DEBUG = LAYER not in ["acceptance", "production"]


INSTALLED_APPS += [
    "service",
    "accounts",
    "lottery",
    "django.contrib.humanize",
    "rest_framework",
]

LOGIN_URL = "accounts:signin"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = LOGIN_URL

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}


# Celery settings for background tasks
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True

# Celery Beat settings - use writable directory
CELERY_BEAT_SCHEDULE_FILENAME = "/tmp/celerybeat-schedule"


# Settings for production deployment
if SITENAME:
    ALLOWED_HOSTS = [SITENAME]
    CSRF_TRUSTED_ORIGINS = [f"https://{SITENAME}"]
    BASE_URL = f"https://{SITENAME}"
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost"]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8080",
        "http://localhost:8081",
        "http://web",
    ]
    BASE_URL = "http://localhost:8000"


DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE or "django.db.backends.sqlite3",
        "NAME": DATABASE_NAME or BASE_DIR.parent / "db.sqlite3",
        "HOST": DATABASE_HOST,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
    }
}


# Extending MIDDLEWARE
def _add_middleware(middleware, after=None):
    try:
        index = max(
            index
            for index, m in enumerate(MIDDLEWARE)
            if m.split(".")[-1] == after
        )
    except ValueError:
        index = len(MIDDLEWARE)
    MIDDLEWARE.insert(index + 1, middleware)


# Whitenoise
STATIC_ROOT = BASE_DIR.parent / "static"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
_add_middleware(
    "whitenoise.middleware.WhiteNoiseMiddleware",
    after="SecurityMiddleware",
)


# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
