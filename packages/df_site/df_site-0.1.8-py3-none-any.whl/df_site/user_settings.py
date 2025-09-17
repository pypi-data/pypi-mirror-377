"""Manage user settings."""

from functools import lru_cache
from typing import Any, Optional

from cookie_consent.util import get_cookie_value_from_request
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Field
from django.forms import Widget
from django.http import HttpRequest, HttpResponse

from df_site.models import AbstractPreferences


@lru_cache
def get_user_instance() -> AbstractPreferences:
    """Return a blank user instance, required for validation purposes."""
    return get_user_model()()


def get_user_setting(
    attr: str, user: Optional[AbstractPreferences] = None, request: Optional[HttpRequest] = None
) -> Any:
    """Return the specified user setting.

    If the user is given, the value is read from the user instance.
    If the cookie provides a value, it is validated and used.
    Otherwise, the default value is returned.
    """
    if user:
        return getattr(user, attr)
    elif request and request.user.is_authenticated:
        return getattr(request.user, attr)
    user_instance = get_user_instance()
    opts = user_instance._meta
    field = opts.get_field(attr)
    raw_value = request.COOKIES.get(attr) if request else None
    value = field.default
    if raw_value is not None:
        try:
            value = field.formfield().clean(raw_value)
        except ValidationError:
            pass
    return value


def set_user_setting(
    attr: str,
    value: Any,
    user: Optional[AbstractPreferences] = None,
    request: Optional[HttpRequest] = None,
    response: Optional[HttpResponse] = None,
) -> None:
    """Set the user's preferences."""
    if user:
        setattr(user, attr, value)
        user.save()
    elif request and request.user.is_authenticated:
        setattr(request.user, attr, value)
        request.user.save()
    elif get_cookie_value_from_request(request, "user-settings"):
        user_instance = get_user_instance()
        opts = user_instance._meta
        field: Field = opts.get_field(attr)
        widget: Widget = field.formfield().hidden_widget()
        raw_value: str = widget.format_value(value)
        response.set_cookie(attr, raw_value, samesite="Strict", secure=settings.USE_SSL)
