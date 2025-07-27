from django.urls import path

from . import api_views


app_name = "lottery_api"

urlpatterns = [
    # Public endpoints (no authentication required)
    path("draws/open/", api_views.OpenDrawsView.as_view(), name="open_draws"),
    path(
        "draws/closed/",
        api_views.ClosedDrawsView.as_view(),
        name="closed_draws",
    ),
    path(
        "draws/<int:pk>/",
        api_views.DrawDetailView.as_view(),
        name="draw_detail",
    ),
    path("stats/", api_views.LotteryStatsView.as_view(), name="lottery_stats"),
    # User-specific endpoints (authentication required)
    path(
        "my-ballots/", api_views.UserBallotsView.as_view(), name="user_ballots"
    ),
    path(
        "my-winnings/",
        api_views.UserWinningsView.as_view(),
        name="user_winnings",
    ),
    path(
        "purchase-ballots/",
        api_views.BallotPurchaseView.as_view(),
        name="purchase_ballots",
    ),
    path(
        "ballots/<int:ballot_id>/assign/",
        api_views.BallotAssignmentView.as_view(),
        name="assign_ballot",
    ),
    path(
        "ballots/<int:pk>/",
        api_views.BallotDetailView.as_view(),
        name="ballot_detail",
    ),
]
