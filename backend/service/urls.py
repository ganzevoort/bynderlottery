"""
URL configuration for lottery service.
"""

from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("lottery/", include("lottery.urls")),
    path("", views.index_view, name="index"),
]
