"""Custom template tags for generating Subresource Integrity hashes for Pipeline assets."""

import base64
import hashlib
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from pipeline.templatetags.pipeline import JavascriptNode, StylesheetNode
from pipeline.utils import guess_type

register = template.Library()


def get_sri(path, method=None):
    """Generate a Subresource Integrity hash for the given file."""
    if method in {"sha256", "sha384", "sha512"} and staticfiles_storage.exists(path):
        with staticfiles_storage.open(path) as fd:
            h = getattr(hashlib, method)()
            for data in iter(lambda: fd.read(16384), b""):
                h.update(data)
        hashed = base64.b64encode(h.digest()).decode()
        return f"{method}-{hashed}"
    return None


if not settings.DEBUG:
    get_sri = lru_cache(maxsize=1024)(get_sri)


class SRIJavascriptNode(JavascriptNode):
    """Render a <script> tag with a SRI hash for the given group."""

    def render_js(self, package, path):
        """Render the JS tag with SRI hash."""
        template_name = package.template_name or "pipeline/js.html"
        context = package.extra_context
        url = mark_safe(staticfiles_storage.url(path))  # noqa
        context.update(
            {
                "type": guess_type(path, "text/javascript"),
                "url": url,
                "crossorigin": "anonymous",
                "integrity": get_sri(path, method=package.config.get("integrity")),
            }
        )
        return render_to_string(template_name, context)


# noinspection PyUnusedLocal
@register.tag
def sri_javascript(parser, token):
    """Generate a <script> tag with a SRI hash for the given group."""
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        tag_name = token.split_contents()[0]
        raise template.TemplateSyntaxError(
            f"{tag_name!r} requires exactly one argument: the name of a group in the PIPELINE.JAVASCRIPT setting"
        )
    return SRIJavascriptNode(name)


class SRIStylesheetNode(StylesheetNode):
    """Render a <link> tag with a SRI hash for the given group."""

    def render_css(self, package, path):
        """Render the CSS tag with SRI hash."""
        template_name = package.template_name or "pipeline/css.html"
        context = package.extra_context
        url = mark_safe(staticfiles_storage.url(path))  # noqa
        context.update(
            {
                "type": guess_type(path, "text/css"),
                "url": url,
                "crossorigin": "anonymous",
                "integrity": get_sri(path, method=package.config.get("integrity")),
            }
        )
        return render_to_string(template_name, context)


# noinspection PyUnusedLocal
@register.tag
def sri_stylesheet(parser, token):
    """Generate a <link> tag with a SRI hash for the given group."""
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        tag_name = token.split_contents()[0]
        raise template.TemplateSyntaxError(
            f"{tag_name!r} requires exactly one argument: the name of a group in the PIPELINE.STYLESHEET setting"
        )
    return SRIStylesheetNode(name)
