import os

__all__ = [
    "LAYER",
    "SITENAME",
    "SECRET_KEY",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
    "DATABASE_ENGINE",
    "DATABASE_HOST",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
    "EMAIL_BACKEND",
    "DEFAULT_FROM_EMAIL",
    "TIME_ZONE",
]

globals().update({envvar: os.getenv(envvar) for envvar in __all__})
