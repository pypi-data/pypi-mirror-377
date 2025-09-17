"""List of URLs for the df_site app."""

from django.conf import settings
from django.urls import path
from django.utils.module_loading import import_string

from df_site.users.views import theme_switch

app_name = "users"
urlpatterns = [
    path("theme-switch", theme_switch, name="theme_switch"),
]
if settings.AUTH_USER_SETTINGS_VIEW:
    user_settings_view = import_string(settings.AUTH_USER_SETTINGS_VIEW)
    urlpatterns.append(
        path("settings", user_settings_view.as_view(), name="settings"),
    )
