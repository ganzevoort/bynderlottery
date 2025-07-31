from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    DrawSerializer,
    DrawDetailSerializer,
    BallotSerializer,
    BallotPurchaseSerializer,
    UserBallotsSerializer,
)
from .models import Draw, Ballot
from accounts.models import Account


@extend_schema(
    tags=["Lottery"],
    summary="List Open Draws",
    description="Get all open draws that are available for ballot assignment",
    responses={
        200: DrawSerializer,
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid request"}
            },
        },
    },
)
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


@extend_schema(
    tags=["Lottery"],
    summary="List Closed Draws",
    description="Get all closed draws with results and winners",
    responses={
        200: DrawDetailSerializer,
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid request"}
            },
        },
    },
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


@extend_schema(
    tags=["Lottery"],
    summary="Get Draw Details",
    description="Get detailed information about a specific draw",
    parameters=[
        OpenApiParameter(
            name="pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Draw ID",
            examples=[
                OpenApiExample("Draw ID", value=1, description="Draw ID")
            ],
        )
    ],
    responses={
        200: DrawDetailSerializer,
        404: {
            "description": "Draw not found",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Draw not found"}
            },
        },
    },
)
class DrawDetailView(generics.RetrieveAPIView):
    """API endpoint for detailed draw information"""

    serializer_class = DrawDetailSerializer
    permission_classes = [AllowAny]
    queryset = Draw.objects.select_related("drawtype").prefetch_related(
        "ballots__account__user", "ballots__prize"
    )


@extend_schema(
    tags=["User Ballots"],
    summary="Get User Ballots",
    description="Get the current user's ballot summary and unassigned ballots",
    responses={
        200: UserBallotsSerializer,
        401: {
            "description": "Unauthorized",
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
)
class UserBallotsView(APIView):
    """API endpoint for user's ballots"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's ballot summary"""
        serializer = UserBallotsSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["User Ballots"],
    summary="Purchase Ballots",
    description="Purchase new ballots for the current user",
    request=BallotPurchaseSerializer,
    responses={
        200: {
            "description": "Ballots purchased successfully",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Successfully purchased 5 ballot(s)",
                },
                "ballots_created": {"type": "integer", "example": 5},
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid quantity"}
            },
        },
        401: {
            "description": "Unauthorized",
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
)
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
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["User Ballots"],
    summary="Assign Ballot to Draw",
    description="Assign a user's ballot to a specific draw",
    parameters=[
        OpenApiParameter(
            name="ballot_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Ballot ID",
            examples=[
                OpenApiExample("Ballot ID", value=1, description="Ballot ID")
            ],
        )
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "draw_id": {
                    "type": "integer",
                    "description": "Draw ID to assign ballot to",
                    "example": 1,
                }
            },
            "required": ["draw_id"],
        }
    },
    responses={
        200: {
            "description": "Ballot assigned successfully",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Ballot assigned to draw successfully",
                }
            },
        },
        400: {
            "description": "Bad request",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid draw ID"}
            },
        },
        404: {
            "description": "Ballot or draw not found",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Ballot not found"}
            },
        },
    },
)
class BallotAssignmentView(APIView):
    """API endpoint for assigning ballots to draws"""

    permission_classes = [IsAuthenticated]

    def post(self, request, ballot_id):
        """Assign ballot to draw"""
        try:
            ballot = get_object_or_404(
                Ballot, id=ballot_id, account__user=request.user
            )
            draw_id = request.data.get("draw_id")

            if not draw_id:
                return Response(
                    {"error": "draw_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                draw = Draw.objects.get(id=draw_id, closed__isnull=True)
            except Draw.DoesNotExist:
                return Response(
                    {"error": "Invalid draw ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if ballot is already assigned
            if ballot.draw:
                return Response(
                    {"error": "Ballot is already assigned to a draw"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Assign ballot to draw
            ballot.draw = draw
            ballot.save()

            return Response(
                {"message": "Ballot assigned to draw successfully"},
                status=status.HTTP_200_OK,
            )

        except Ballot.DoesNotExist:
            return Response(
                {"error": "Ballot not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@extend_schema(
    tags=["User Ballots"],
    summary="Get Ballot Details",
    description="Get detailed information about a specific ballot",
    parameters=[
        OpenApiParameter(
            name="pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Ballot ID",
            examples=[
                OpenApiExample("Ballot ID", value=1, description="Ballot ID")
            ],
        )
    ],
    responses={
        200: BallotSerializer,
        404: {
            "description": "Ballot not found",
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Ballot not found"}
            },
        },
    },
)
class BallotDetailView(generics.RetrieveAPIView):
    """API endpoint for individual ballot details"""

    serializer_class = BallotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get ballots for the current user"""
        return Ballot.objects.filter(account__user=self.request.user)


@extend_schema(
    tags=["User Winnings"],
    summary="Get User Winnings",
    description="Get the current user's winnings summary",
    responses={
        200: {
            "description": "User winnings summary",
            "type": "object",
            "properties": {
                "total_winnings": {"type": "integer", "example": 100000},
                "total_winning_ballots": {"type": "integer", "example": 3},
                "winnings_by_draw": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "draw": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer", "example": 1},
                                    "drawtype_name": {
                                        "type": "string",
                                        "example": "Daily",
                                    },
                                    "date": {
                                        "type": "string",
                                        "format": "date",
                                        "example": "2025-07-28",
                                    },
                                },
                            },
                            "prizes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "prize_name": {
                                            "type": "string",
                                            "example": "Jackpot",
                                        },
                                        "prize_amount": {
                                            "type": "integer",
                                            "example": 100000,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        401: {
            "description": "Unauthorized",
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "Authentication credentials were not provided.",
                }
            },
        },
    },
)
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


@extend_schema(
    tags=["Lottery Statistics"],
    summary="Get Lottery Statistics",
    description=(
        "Get public lottery statistics including draws, prizes, "
        "and recent winners"
    ),
    responses={
        200: {
            "description": "Lottery statistics",
            "type": "object",
            "properties": {
                "total_draws": {"type": "integer", "example": 5},
                "open_draws": {"type": "integer", "example": 3},
                "closed_draws": {"type": "integer", "example": 1},
                "total_prizes_awarded": {"type": "integer", "example": 1},
                "total_amount_awarded": {"type": "integer", "example": 100000},
                "recent_winners": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "draw": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer", "example": 1},
                                    "drawtype_name": {
                                        "type": "string",
                                        "example": "Daily",
                                    },
                                    "date": {
                                        "type": "string",
                                        "format": "date",
                                        "example": "2025-07-28",
                                    },
                                },
                            },
                            "winners": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "example": "John Doe",
                                        },
                                        "prize_name": {
                                            "type": "string",
                                            "example": "Jackpot",
                                        },
                                        "prize_amount": {
                                            "type": "integer",
                                            "example": 100000,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
    },
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
