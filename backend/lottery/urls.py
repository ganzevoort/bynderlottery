from django.urls import path
from . import views

app_name = "lottery"

urlpatterns = [
    path("", views.OpenDrawsListView.as_view(), name="open_draws"),
    path("closed/", views.ClosedDrawsListView.as_view(), name="closed_draws"),
    path("my-ballots/", views.UserBallotsView.as_view(), name="user_ballots"),
    path(
        "assign-ballot/<int:ballot_id>/",
        views.AssignBallotView.as_view(),
        name="assign_ballot",
    ),
]
