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
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_USE_TLS",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "DEFAULT_FROM_EMAIL",
    "TIME_ZONE",
    "REDIS_HOST",
    "REDIS_PORT",
]

globals().update({envvar: os.getenv(envvar) for envvar in __all__})
