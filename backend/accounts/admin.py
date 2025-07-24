from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "get_name",
        "get_email",
        "email_verified",
        "created_at",
    )
    list_filter = ("email_verified", "created_at")
    search_fields = ("user__last_name", "user__email", "bankaccount")
    readonly_fields = ("created_at", "updated_at")

    def get_name(self, obj):
        return obj.user.get_full_name()

    get_name.short_description = "Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"

    fieldsets = (
        (
            "User Information",
            {"fields": ("user", "bankaccount")},
        ),
        (
            "Email Verification",
            {
                "fields": ("email_verified", "email_verification_token"),
                "classes": ("collapse",),
            },
        ),
        (
            "Password Reset",
            {
                "fields": ("password_reset_token", "password_reset_expires"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class AccountInline(admin.StackedInline):
    model = Account
    extra = 0
    fields = ("bankaccount", "email_verified")
    verbose_name = "Account"
    verbose_name_plural = "Accounts"


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline,)
