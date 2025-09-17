"""List of URLs for the df_site app."""

from django.conf import settings
from django.urls import include, path
from django.utils.module_loading import import_string
from django.views.generic import RedirectView
from django_prometheus import exports

from df_site.views import (
    BrowserConfigView,
    HumansTxtView,
    SecurityTxtView,
    csp_report_view,
    security_gpg_view,
    site_webmanifest_view,
    thumbnail_view,
)

urlpatterns = [
    path(
        ".well-known/change-password",
        RedirectView.as_view(pattern_name="account_change_password", permanent=True),
        name="well-known-change-password",
    ),
    path(".well-known/security.txt", SecurityTxtView.as_view(), name="well-known-security"),
    path(".well-known/humans.txt", HumansTxtView.as_view(), name="well-known-humans"),
    path(".well-known/gpg.txt", security_gpg_view, name="well-known-gpg"),
    path("site.webmanifest", site_webmanifest_view, name="site_webmanifest"),
    path("browserconfig.xml", BrowserConfigView.as_view(), name="browserconfig"),
    path("metrics", exports.ExportToDjangoView, name="prometheus-django-metrics"),
    path(settings.CSP_REPORT_URI[1:], csp_report_view, name="csp_report"),
    path("users/", include("df_site.users.urls", namespace="users")),
    path("thumbnails/<path:path>", thumbnail_view, name="thumbnails"),
    path("messages/", include("df_site.postman.urls", namespace="postman")),
    path("cookies/", include("cookie_consent.urls")),
    path(
        "upload_file/",
        import_string(settings.CK_EDITOR_5_UPLOAD_FILE_VIEW),
        name=settings.CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME,
    ),
]
