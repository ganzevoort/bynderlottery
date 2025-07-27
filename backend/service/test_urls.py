from django.urls import path

from . import test_views


# Test endpoints for Cypress (only in test layer)
urlpatterns = [
    path("clear-database/", test_views.clear_database, name="clear_database"),
    path("seed-data/", test_views.seed_test_data, name="seed_test_data"),
    path("verify-user/", test_views.verify_user, name="verify_user"),
    path(
        "health-check/", test_views.test_health_check, name="test_health_check"
    ),
    path("get-tokens/", test_views.get_test_tokens, name="get_test_tokens"),
]
