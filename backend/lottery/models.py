from django.db import models
from ordered_model.models import OrderedModel

from accounts.models import Account


class DrawType(OrderedModel):
    """
    This will represent daily, weekly, newyears-eve lottery drawtypes.

    schedule can be {}, {"weekday": 6} or {"month": 12, "day": 31}.
    """

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    schedule = models.JSONField(default=dict)

    def __str__(self):
        return self.name

    def schedule_matches(self, date):
        if not isinstance(self.schedule, dict):
            return False
        for selector, selected_value in self.schedule.items():
            actual_value = getattr(date, selector, None)
            if callable(actual_value):
                actual_value = actual_value()
            if actual_value != selected_value:
                return False
        return True

    @classmethod
    def type_for_date(cls, date):
        """
        Returns the draw type for a specific date.
        The highest ordered drawtype with a schedule matching the date
        is returned.
        """
        for drawtype in cls.objects.filter(is_active=True).order_by("-order"):
            if drawtype.schedule_matches(date):
                return drawtype
        return None


class Prize(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField()
    number = models.IntegerField(default=1)
    drawtype = models.ForeignKey(
        DrawType, on_delete=models.CASCADE, related_name="prizes"
    )

    def __str__(self):
        return f"{self.name}: {self.number}x € {self.amount:,}"

    class Meta:
        ordering = ("drawtype", "-amount", "number")


class Draw(models.Model):
    drawtype = models.ForeignKey(
        DrawType, on_delete=models.PROTECT, related_name="draws"
    )
    date = models.DateField(unique=True)
    closed = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.drawtype_id:
            self.drawtype = DrawType.type_for_date(self.date)
        super().save(*args, **kwargs)

    def __str__(self):
        formatted = f"{self.drawtype.name} - {self.date}"
        if self.closed:
            formatted += " (closed)"
        return formatted

    class Meta:
        ordering = ("date",)


class Ballot(models.Model):
    draw = models.ForeignKey(
        Draw,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ballots",
    )
    account = models.ForeignKey(
        Account, null=False, on_delete=models.PROTECT, related_name="ballots"
    )
    prize = models.ForeignKey(
        Prize,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ballots",
    )

    def __str__(self):
        return (
            f"{self.draw.date if self.draw else 'unassigned'} - "
            f"{self.account.user.get_full_name()}"
        )

    class Meta:
        ordering = ("draw", "account")
