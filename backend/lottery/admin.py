from django.contrib import admin
from ordered_model.admin import OrderedInlineModelAdminMixin

from .models import DrawType, Prize, Draw, Ballot


class PrizeInline(admin.TabularInline):
    model = Prize
    extra = 1


@admin.register(DrawType)
class DrawTypeAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ("name", "is_active", "get_prizes")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("order",)
    inlines = [PrizeInline]

    def get_prizes(self, obj):
        return ", ".join(str(prize) for prize in obj.prizes.all())

    get_prizes.short_description = "Prizes"


class BallotInline(admin.TabularInline):
    model = Ballot
    extra = 1
    readonly_fields = ("account", "prize")
    list_display = ("account", "prize")
    list_filter = ("prize",)
    search_fields = (
        "account__user__first_name",
        "account__user__last_name",
        "account__user__email",
    )


@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    list_display = ("date", "drawtype", "closed")
    list_filter = ("drawtype", "closed")
    search_fields = ("date",)
    date_hierarchy = "date"
    inlines = [BallotInline]
