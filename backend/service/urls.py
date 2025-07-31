"""
URL configuration for lottery service.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("oldstyle/accounts/", include("accounts.urls")),
    path("oldstyle/lottery/", include("lottery.urls")),
    path("oldstyle/", views.index_view, name="index"),
    path("api/accounts/", include("accounts.api_urls")),
    path("api/lottery/", include("lottery.api_urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


# Test endpoints for Cypress (only in test layer)
if settings.LAYER == "test":
    urlpatterns.append(path("api/test/", include("service.test_urls")))
