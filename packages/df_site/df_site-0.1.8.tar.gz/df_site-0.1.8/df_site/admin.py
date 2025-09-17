"""Admin classes for the df_site app."""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from df_site.models import AlertRibbon, PreferencesUser


@admin.register(AlertRibbon)
class AlertRibbonAdmin(admin.ModelAdmin):
    """Admin class for the alert ribbon model."""

    list_display = ("message", "color", "start_date", "end_date", "is_active")
    list_filter = ("color", "start_date", "end_date", "is_active", "position")
    search_fields = ("summary",)
    fields = ["summary", "url", "message", "color", "start_date", "end_date", "is_active", "position"]


if "allauth.account" in settings.INSTALLED_APPS:
    from allauth.account.models import EmailAddress

    class EmailAddressInline(admin.TabularInline):
        """Inline for the email address model."""

        model = EmailAddress
        extra = 0
else:
    EmailAddressInline = None

if "allauth.mfa" in settings.INSTALLED_APPS:
    from allauth.mfa.models import Authenticator

    class AuthenticatorInline(admin.TabularInline):
        """Inline for the authenticator model."""

        model = Authenticator
        extra = 0
        fields = ["type", "created_at", "last_used_at"]
        readonly_fields = ["type", "created_at", "last_used_at"]

        def has_add_permission(self, request, obj):
            """Return False to prevent adding new authenticators."""
            return False
else:
    AuthenticatorInline = None

if "allauth.socialaccount" in settings.INSTALLED_APPS:
    from allauth.socialaccount.models import SocialAccount

    class SocialAccountInline(admin.TabularInline):
        """Inline for the social account model."""

        model = SocialAccount
        extra = 0
        fields = ["provider", "last_login", "date_joined"]
        readonly_fields = ["provider", "last_login", "date_joined"]

        def has_add_permission(self, request_, obj_):
            """Return False to prevent adding new social accounts."""
            return False
else:
    SocialAccountInline = None

if "allauth.usersessions" in settings.INSTALLED_APPS:
    from allauth.usersessions.models import UserSession

    class UserSessionInline(admin.TabularInline):
        """Inline for the user session model."""

        model = UserSession
        extra = 0
        fields = [
            "created_at",
            "ip",
            "last_seen_at",
        ]
        readonly_fields = [
            "created_at",
            "ip",
            "last_seen_at",
        ]

        def has_add_permission(self, request_, obj):
            """Return False to prevent adding new user sessions."""
            return False
else:
    UserSessionInline = None


@admin.register(PreferencesUser)
class PreferencesUserAdmin(UserAdmin):
    """Admin class for the preferences user model."""

    inlines = []
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined", "groups")
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "color_theme", "display_online", "email_notifications")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": (("last_login", "date_joined"),)}),
    )

    def get_inlines(self, request, obj):
        """Return inlines excluding those that correspond to apps not installed."""
        inlines = [EmailAddressInline, AuthenticatorInline, SocialAccountInline, UserSessionInline]
        if obj is None:
            return []
        inlines = [x for x in inlines if x is not None]
        return inlines
