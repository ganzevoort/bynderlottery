from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .serializers import (
    DrawSerializer,
    DrawDetailSerializer,
    BallotSerializer,
    BallotPurchaseSerializer,
    BallotAssignmentSerializer,
    UserBallotsSerializer,
)
from .models import Draw, Ballot
from accounts.models import Account


class OpenDrawsView(generics.ListAPIView):
    """API endpoint for listing open draws"""

    serializer_class = DrawSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get open draws ordered by date"""
        return (
            Draw.objects.filter(
                closed__isnull=True, date__gte=timezone.now().date()
            )
            .select_related("drawtype")
            .order_by("date")
        )


class ClosedDrawsView(generics.ListAPIView):
    """API endpoint for listing closed draws"""

    serializer_class = DrawDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get closed draws ordered by date (newest first)"""
        return (
            Draw.objects.filter(closed__isnull=False)
            .select_related("drawtype")
            .prefetch_related("ballots__account__user", "ballots__prize")
            .order_by("-date")
        )


class DrawDetailView(generics.RetrieveAPIView):
    """API endpoint for detailed draw information"""

    serializer_class = DrawDetailSerializer
    permission_classes = [AllowAny]
    queryset = Draw.objects.select_related("drawtype").prefetch_related(
        "ballots__account__user", "ballots__prize"
    )


class UserBallotsView(APIView):
    """API endpoint for user's ballots"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's ballot summary"""
        serializer = UserBallotsSerializer(request.user)
        return Response(serializer.data)


class BallotPurchaseView(APIView):
    """API endpoint for purchasing ballots"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Purchase ballots (mock implementation)"""
        serializer = BallotPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data["quantity"]

            # Mock payment processing
            # In a real implementation, this would integrate with a
            # payment processor
            # Get or create user's account
            account, created = Account.objects.get_or_create(user=request.user)

            # Create ballots for the user
            ballots = []
            for _ in range(quantity):
                ballot = Ballot.objects.create(account=account)
                ballots.append(ballot)

            return Response(
                {
                    "message": f"Successfully purchased {quantity} ballot(s)",
                    "ballots_created": len(ballots),
                    "total_ballots": Ballot.objects.filter(
                        account__user=request.user
                    ).count(),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BallotAssignmentView(APIView):
    """API endpoint for assigning ballots to draws"""

    permission_classes = [IsAuthenticated]

    def post(self, request, ballot_id):
        """Assign a ballot to a draw"""
        # Get the ballot and ensure it belongs to the user
        ballot = get_object_or_404(
            Ballot, id=ballot_id, account__user=request.user
        )

        # Check if ballot is already assigned
        if ballot.draw:
            return Response(
                {"error": "Ballot is already assigned to a draw"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BallotAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            draw_id = serializer.validated_data["draw_id"]
            draw = get_object_or_404(Draw, id=draw_id)

            # Assign ballot to draw
            ballot.draw = draw
            ballot.save()

            return Response(
                {
                    "message": f"Ballot successfully assigned to {draw}",
                    "ballot_id": ballot.id,
                    "draw_id": draw.id,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BallotDetailView(generics.RetrieveAPIView):
    """API endpoint for individual ballot details"""

    serializer_class = BallotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only show ballots belonging to the authenticated user"""
        return Ballot.objects.filter(
            account__user=self.request.user
        ).select_related("draw", "prize")


class UserWinningsView(APIView):
    """API endpoint for user's winnings summary"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's winnings summary"""
        winning_ballots = (
            Ballot.objects.filter(
                account__user=request.user, prize__isnull=False
            )
            .select_related("draw", "prize")
            .order_by("-draw__date")
        )

        total_winnings = sum(ballot.prize.amount for ballot in winning_ballots)

        winnings_by_draw = {}
        for ballot in winning_ballots:
            draw_id = ballot.draw.id
            if draw_id not in winnings_by_draw:
                winnings_by_draw[draw_id] = {
                    "draw": {
                        "id": ballot.draw.id,
                        "drawtype_name": ballot.draw.drawtype.name,
                        "date": ballot.draw.date,
                    },
                    "prizes": [],
                }
            winnings_by_draw[draw_id]["prizes"].append(
                {
                    "prize_name": ballot.prize.name,
                    "prize_amount": ballot.prize.amount,
                }
            )

        return Response(
            {
                "total_winnings": total_winnings,
                "total_winning_ballots": len(winning_ballots),
                "winnings_by_draw": list(winnings_by_draw.values()),
            }
        )


class LotteryStatsView(APIView):
    """API endpoint for lottery statistics"""

    permission_classes = [AllowAny]

    def get(self, request):
        """Get public lottery statistics"""
        total_draws = Draw.objects.count()
        open_draws = Draw.objects.filter(
            closed__isnull=True, date__gte=timezone.now().date()
        ).count()
        closed_draws = Draw.objects.filter(closed__isnull=False).count()

        # Total prizes awarded
        total_prizes_awarded = Ballot.objects.filter(
            prize__isnull=False
        ).count()
        total_amount_awarded = sum(
            ballot.prize.amount
            for ballot in Ballot.objects.filter(prize__isnull=False)
        )

        # Recent winners (last 5 closed draws)
        recent_draws = Draw.objects.filter(closed__isnull=False).order_by(
            "-date"
        )[:5]
        recent_winners = []
        for draw in recent_draws:
            draw_winners = []
            for ballot in draw.ballots.filter(
                prize__isnull=False
            ).select_related("account__user", "prize"):
                draw_winners.append(
                    {
                        "name": ballot.account.user.last_name,
                        "prize_name": ballot.prize.name,
                        "prize_amount": ballot.prize.amount,
                    }
                )
            if draw_winners:
                recent_winners.append(
                    {
                        "draw": {
                            "id": draw.id,
                            "drawtype_name": draw.drawtype.name,
                            "date": draw.date,
                        },
                        "winners": draw_winners,
                    }
                )

        return Response(
            {
                "total_draws": total_draws,
                "open_draws": open_draws,
                "closed_draws": closed_draws,
                "total_prizes_awarded": total_prizes_awarded,
                "total_amount_awarded": total_amount_awarded,
                "recent_winners": recent_winners,
            }
        )
