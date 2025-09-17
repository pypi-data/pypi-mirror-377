"""Views for the df_site app."""

import datetime
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.static import serve

from df_site.templatetags.df_site import abs_url
from df_site.templatetags.images import CachedImage

logger = logging.getLogger(__name__)


def site_webmanifest_view(request: HttpRequest) -> HttpResponse:
    """Generate a site.webmanifest view."""
    result = {
        "name": settings.DF_SITE_TITLE,
        "short_name": settings.DF_SITE_TITLE,
        "icons": [
            {"src": static("favicon/android-chrome-192x192.png"), "sizes": "192x192", "type": "image/png"},
            {"src": static("favicon/android-chrome-512x512.png"), "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": settings.DF_ANDROID_THEME_COLOR,
        "background_color": settings.DF_ANDROID_BACKGROUND_COLOR,
        "display": "standalone",
    }
    return JsonResponse(result)


@csrf_exempt
def csp_report_view(request: HttpRequest) -> HttpResponse:
    """View to receive CSP reports, displaying them to the user in DEBUG mode."""
    logger.info("CSP report: %s", request.body)
    if settings.DEBUG:
        try:
            content = json.loads(request.body)
            csp_report = content["csp-report"]
            msg = (
                f"<strong>CSP violation</strong> on this <a href='{csp_report['document-uri']}'>page</a>:"
                f" {csp_report['effective-directive']} forbids the use of"
                f" '{csp_report['blocked-uri']}' URIs."
            )
            messages.error(request, mark_safe(msg))  # noqa
        except ValueError:
            pass
    return HttpResponse(status=204)


class BrowserConfigView(TemplateView):
    """View for the browserconfig.xml file."""

    template_name = "favicon/browserconfig.xml"
    content_type = "application/xml"


def security_gpg_view(request: HttpRequest) -> HttpResponse:
    """Return the GPG key to communicate with about security problems."""
    if settings.DF_SITE_SECURITY_GPG_CONTENT:
        raise Http404
    response = HttpResponse(settings.DF_SITE_SECURITY_GPG_CONTENT, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="gpg.txt"'
    return response


class SecurityTxtView(TemplateView):
    """View for the ./well-known/security.txt file."""

    template_name = "df_site/security.txt"
    content_type = "plain/text"

    def get_context_data(self, **kwargs):
        """Return the context data for the view."""
        context = super().get_context_data(**kwargs)
        context["security_txt_path"] = abs_url(reverse("well-known-security"))
        context["security_email"] = settings.DF_SITE_SECURITY_EMAIL
        context["security_language_code"] = settings.DF_SITE_SECURITY_LANGUAGE_CODE
        gpg_key = None
        if settings.DF_SITE_SECURITY_GPG_CONTENT:
            gpg_key = abs_url(reverse("well-known-gpg"))
        context["security_gpg_key"] = gpg_key
        now = datetime.datetime.now(tz=datetime.UTC)
        now = now - datetime.timedelta(microseconds=now.microsecond)
        context["security_expires"] = now + datetime.timedelta(days=30)
        return context


class HumansTxtView(TemplateView):
    """View for the ./well-known/humans.txt file."""

    template_name = "df_site/humans.txt"
    content_type = "plain/text"

    def get_context_data(self, **kwargs):
        """Return the context data for the view."""
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now(tz=datetime.UTC)
        now = now - datetime.timedelta(microseconds=now.microsecond)
        context["humans_description"] = settings.DF_SITE_DESCRIPTION
        context["humans_social_networks"] = settings.DF_SITE_SOCIAL_NETWORKS
        context["humans_keywords"] = settings.DF_SITE_KEYWORDS
        context["humans_update"] = now
        return context


def thumbnail_view(request: HttpRequest, path: str) -> HttpResponse:
    """Return a thumbnail image."""
    img = CachedImage.from_target_path(path)
    if not img.src_storage_obj.exists(path):
        img.process()
    return serve(request, path=path, document_root=settings.STATIC_ROOT)


#
