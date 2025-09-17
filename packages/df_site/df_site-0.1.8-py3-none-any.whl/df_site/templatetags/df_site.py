"""Custom template tags for the df_site app."""

import datetime
import re
from html import escape
from typing import Dict, List, Optional, Union

from django import template
from django.conf import settings
from django.contrib.admin.views.main import PAGE_VAR
from django.core.paginator import Paginator
from django.template.base import kwarg_re
from django.template.defaultfilters import date
from django.template.defaulttags import URLNode
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from df_site.components.base import Component
from df_site.constants import BRAND_ICONS, INT_RE

register = template.Library()


@register.filter()
def abs_url(value):
    """Given a relative URL, return an absolute URL."""
    if value and value.startswith("/"):
        base_url = settings.SERVER_BASE_URL
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        return mark_safe(f"{base_url}{value}")  # noqa
    return value


class AbsoluteURLNode(URLNode):
    """A template node that renders an absolute URL."""

    def render(self, context):
        """Render the URL node prefixed with the server base URL."""
        rendered = super().render(context)
        return abs_url(rendered)


@register.simple_tag(takes_context=True)
def paginate_qs(context, queryset, per_page=10, page_attr="page"):
    """Paginate a queryset and store the pagination in the context."""
    paginator = Paginator(queryset, per_page)
    page_number = context["request"].GET.get(page_attr, "1")
    if INT_RE.match(page_number):
        page = paginator.get_page(int(page_number))
    else:
        page = paginator.get_page(1)
    return page


@register.tag(name="abs_url")
def abs_url_tag(parser, token):
    """Like the default Django's url tag, but return absolute URLs."""
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(f"'{bits[0]}' takes at least one argument, a URL pattern name.")
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))
    return AbsoluteURLNode(viewname, args, kwargs, asvar)


@register.filter
def fa6_allauth_icon(provider_id):
    """Return the font-awesome icon name for a given allauth provider."""
    return BRAND_ICONS.get(provider_id, "key")


@register.simple_tag
def fa6_icon(
    name,
    prefix="fa",
    large: Union[int, bool] = False,
    fixed: bool = False,
    spin: bool = False,
    li: bool = False,
    rotate: Union[int, bool] = None,
    border: bool = False,
    color: str = None,
):
    """Add font-awesome icons in your HTML code."""
    if isinstance(large, int) and 2 <= large <= 5:
        large = f" fa-{large:d}x"
    elif large:
        large = " fa-lg"
    else:
        large = ""
    content = '<i class="{prefix} fa-{name}{large}{fixed}{spin}{li}{rotate}{border}{color}"></i>'.format(
        prefix=prefix,
        name=name,
        large=large,
        fixed=" fa-fw" if fixed else "",
        spin=" fa-spin" if spin else "",
        li=" fa-li" if li else "",
        rotate=f" fa-rotate-{rotate}" if rotate else "",
        border=" fa-border" if border else "",
        color=f"text-{color}" if color else "",
    )
    return mark_safe(content)  # noqa


@register.simple_tag
def bootstrap_breadcrumb(
    breadcrumbs: List[Dict[str, Union[str, bool]]], last_active: bool = True, extra_classes: str = ""
):
    """Render an breadcrumb.

    **Tag name**::

        bootstrap_breadcrumb

    **Parameters**::

        breadcrumbs
            List of dictionaries with the following keys:
                `link`: URL to link to
                `title`: Text to display
                `active`: boolean, element is active, meaning that the link is not displayed

        last_active
            boolean, last element is the active one

            :default: ``True``

        extra_classes
            string, extra CSS classes for elements

            :default: ""

    **Usage**::

        {% bootstrap_breadcrumb [{content}] %}

    **Example**::

        {% bootstrap_breadcrumb crumbs %}
    """
    context = {
        "breadcrumbs": breadcrumbs,
        "last_active": last_active,
        "extra_classes": extra_classes,
    }
    content = render_to_string("django_bootstrap5/breadcrumb.html", context)
    return mark_safe(content)  # noqa S308


@register.simple_tag(takes_context=True)
def component(context, comp: Component, **kwargs):
    """Render a HTML component in a template."""
    text = comp.render(context, **kwargs)
    return mark_safe(text)  # noqa S308


@register.simple_tag
def component_list_url(cl, page: Optional[int] = None):
    """Generate an individual page index link in a paginated list."""
    kwargs = {}
    if page is not None:
        kwargs[PAGE_VAR] = page
    return cl.get_query_string(kwargs)


auto_pill_re = re.compile(r"^(.*)\((\d+)\)\s*$")


@register.simple_tag
def component_auto_badge(
    value: str, color: str = "primary", extra_class: str = "rounded-pill", regex: re.Pattern = auto_pill_re
):
    """Automatically extracts suffixes between parenthesis `(.*)` and put them into badges."""
    if hasattr(value, "__html__"):
        raw_value = str(value)
    else:
        raw_value = escape(str(value))
    if match := regex.match(raw_value):
        prefix = match.group(1)
        suffix = match.group(2)
        new_value = f'{prefix}<span class="badge text-bg-{color} {extra_class}">{suffix}</span>'
        value = mark_safe(new_value)  # noqa S308
    return value


@register.simple_tag
@register.filter
def schema_date(
    value_: Optional[Union[datetime.date, datetime.datetime, datetime.timedelta]], fmt_: Optional[str] = None, **kwargs
):
    """Show a date in a <time></time> element.

    Can be used as a filter or as a tag. In the latter case, value and format are the first two arguments.
    Extra arguments are passed as attributes to the generated HTML.

    `{% schema_date value_ fmt_ itemprop="start" %}` is rendered as
        `<time itemprop="start" datetime="date">date</time>`
    `{{ value_|schema_date:fmt_ }}` is rendered as `<time datetime="date">date</time>`
    """
    content = date(value_, fmt_)
    if isinstance(value_, datetime.date):
        kwargs["datetime"] = value_.strftime("%Y-%m-%d")
    elif isinstance(value_, datetime.datetime):
        kwargs["datetime"] = value_.isoformat()
    elif isinstance(value_, datetime.timedelta):
        attr = "P"
        ts = value_.total_seconds()
        days = int(ts // 86400)
        ts %= 86400
        attr += f"{days}D"
        hours = int(ts // 3600)
        ts %= 3600
        attr += f"{hours}H"
        minutes = int(ts // 60)
        ts %= 60
        attr += f"{minutes}M{ts}S"
        kwargs["datetime"] = attr
    else:
        return content
    escaped = {escape(k): escape(v) for k, v in kwargs.items()}
    attr = " ".join(f'{k}="{v}"' for k, v in escaped.items())
    msg = f"<time {attr}>{content}</time>"
    return mark_safe(msg)  # noqa S308
