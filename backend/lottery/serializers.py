from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DrawType, Draw, Prize, Ballot


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for winner information (name only)"""

    name = serializers.CharField(source="last_name")

    class Meta:
        model = User
        fields = ["name"]


class DrawTypeSerializer(serializers.ModelSerializer):
    """Serializer for DrawType model"""

    class Meta:
        model = DrawType
        fields = ["id", "name", "is_active", "schedule"]


class PrizeSerializer(serializers.ModelSerializer):
    """Serializer for Prize model"""

    class Meta:
        model = Prize
        fields = ["id", "name", "amount", "number", "drawtype"]


class DrawSerializer(serializers.ModelSerializer):
    """Serializer for Draw model"""

    drawtype = DrawTypeSerializer(read_only=True)
    prizes = serializers.SerializerMethodField()
    winner_count = serializers.SerializerMethodField()
    total_prize_amount = serializers.SerializerMethodField()

    class Meta:
        model = Draw
        fields = [
            "id",
            "drawtype",
            "date",
            "closed",
            "ballots",
            "prizes",
            "winner_count",
            "total_prize_amount",
        ]

    def get_prizes(self, obj):
        """Get prizes for this draw's drawtype"""
        return PrizeSerializer(obj.drawtype.prizes.all(), many=True).data

    def get_winner_count(self, obj):
        """Get count of unique winners"""
        if obj.closed:
            return (
                obj.ballots.filter(prize__isnull=False)
                .values("account__user")
                .distinct()
                .count()
            )
        return 0

    def get_total_prize_amount(self, obj):
        """Get total prize amount for this draw"""
        if obj.closed:
            return sum(
                ballot.prize.amount
                for ballot in obj.ballots.filter(prize__isnull=False)
            )
        return 0


class DrawDetailSerializer(DrawSerializer):
    """Detailed serializer for Draw model with winner information"""

    winners = serializers.SerializerMethodField()

    class Meta(DrawSerializer.Meta):
        fields = DrawSerializer.Meta.fields + ["winners"]

    def get_winners(self, obj):
        """Get winner information (name and prize amount only)"""
        if not obj.closed:
            return []

        winners = []
        for ballot in obj.ballots.filter(prize__isnull=False).select_related(
            "account__user", "prize"
        ):
            winners.append(
                {
                    "name": ballot.account.user.last_name,
                    "prize_name": ballot.prize.name,
                    "prize_amount": ballot.prize.amount,
                }
            )
        return winners


class BallotSerializer(serializers.ModelSerializer):
    """Serializer for Ballot model"""

    draw = DrawSerializer(read_only=True)
    prize = PrizeSerializer(read_only=True)

    class Meta:
        model = Ballot
        fields = ["id", "draw", "prize"]


class BallotPurchaseSerializer(serializers.Serializer):
    """Serializer for ballot purchase"""

    quantity = serializers.IntegerField(min_value=1, max_value=100)
    card_number = serializers.CharField(max_length=19)
    expiry_month = serializers.IntegerField(min_value=1, max_value=12)
    expiry_year = serializers.IntegerField(min_value=2025, max_value=2030)
    cvv = serializers.CharField(max_length=4, min_length=3)

    def validate_card_number(self, value):
        """Basic card number validation (mock)"""
        if not value.replace(" ", "").isdigit():
            raise serializers.ValidationError(
                "Card number must contain only digits"
            )
        return value

    def validate_cvv(self, value):
        """Basic CVV validation"""
        if not value.isdigit():
            raise serializers.ValidationError("CVV must contain only digits")
        return value


class BallotAssignmentSerializer(serializers.Serializer):
    """Serializer for ballot assignment to draw"""

    draw_id = serializers.IntegerField()

    def validate_draw_id(self, value):
        """Validate that the draw exists and is open"""
        try:
            draw = Draw.objects.get(id=value)
            if draw.closed:
                raise serializers.ValidationError(
                    "Cannot assign ballot to a closed draw"
                )
            return value
        except Draw.DoesNotExist:
            raise serializers.ValidationError("Draw does not exist")


class UserBallotsSerializer(serializers.Serializer):
    """Serializer for user's ballot summary"""

    unassigned_ballots = serializers.SerializerMethodField()
    assigned_ballots = serializers.SerializerMethodField()
    total_ballots = serializers.SerializerMethodField()

    def get_unassigned_ballots(self, obj):
        """Get unassigned ballots for the user"""
        ballots = Ballot.objects.filter(
            account__user=obj, draw__isnull=True
        ).order_by("-id")
        return BallotSerializer(ballots, many=True).data

    def get_assigned_ballots(self, obj):
        """Get assigned ballots as a flat list"""
        assigned_ballots = (
            Ballot.objects.filter(account__user=obj, draw__isnull=False)
            .select_related("draw", "prize")
            .order_by("-draw__date", "-id")
        )
        return BallotSerializer(assigned_ballots, many=True).data

    def get_total_ballots(self, obj):
        """Get total ballot count for user"""
        return Ballot.objects.filter(account__user=obj).count()
