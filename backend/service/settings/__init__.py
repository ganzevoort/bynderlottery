import os

from .defaults import *
from .environment import *


INSTALLED_APPS += [
    "service",
    "accounts",
    "lottery",
    "django.contrib.humanize",
]

LOGIN_URL = "/accounts/signin/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = LOGIN_URL


# Settings for production deployment
if SITENAME:
    ALLOWED_HOSTS = [SITENAME]
    CSRF_TRUSTED_ORIGINS = [f"https://{SITENAME}"]
    BASE_URL = f"https://{SITENAME}"
else:
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
LOGDIR = BASE_DIR.parent / "logs"
LOGGING = {
    "version": 1,
    "formatters": {
        "simple": {"format": "%(asctime)s %(message)s"},
        "verbose": {
            "format": "%(levelname)s %(asctime)s "
            "%(module)s %(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "requestlog": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 1,
            "filename": os.path.join(LOGDIR, "requests.log"),
            "formatter": "",
        },
        "dblog": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 1,
            "filename": os.path.join(LOGDIR, "db.log"),
            "formatter": "",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["requestlog"],
            "level": "INFO",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["dblog"],
            "level": "DEBUG",
            "propagate": True,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "service": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
