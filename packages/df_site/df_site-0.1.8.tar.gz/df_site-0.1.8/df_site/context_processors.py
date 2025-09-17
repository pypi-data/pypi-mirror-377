"""Define the context processors with global variables about the site."""

import datetime
import logging
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.utils.timezone import now

from df_site.models import AlertRibbon
from df_site.user_settings import get_user_setting

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_current_ribbons(current_date: datetime.datetime) -> Iterable[AlertRibbon]:
    """Get the active ribbons for the current date.

    The current date will be rounded to the nearest hour.
    """
    return list(
        AlertRibbon.objects.filter(
            Q(Q(end_date__gte=current_date) & Q(end_date__isnull=False)) | Q(end_date__isnull=True),
            Q(Q(start_date__lte=current_date) & Q(start_date__isnull=False)) | Q(start_date__isnull=True),
            is_active=True,
        )
    )


def global_site_infos(request: HttpRequest, current_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """Adds a few values to the request context."""
    try:
        color_theme = get_user_setting("color_theme", request=request)
    except Exception as e:
        logger.error("Error getting color theme: %s", e)
        color_theme = settings.DF_SITE_THEMES[0][0]
    if current_date is None:
        current_date = now()
    current_date = current_date.replace(minute=0, second=0, microsecond=0)
    ribbons = get_current_ribbons(current_date)
    x_url = settings.DF_SITE_SOCIAL_NETWORKS.get("twitter", "")
    __, __, df_site_x_account = x_url.rpartition("/")
    return {
        "DF_SITE_TITLE": settings.DF_SITE_TITLE,
        "DF_SITE_DESCRIPTION": settings.DF_SITE_DESCRIPTION,
        "DF_SITE_KEYWORDS": settings.DF_SITE_KEYWORDS,
        "DF_SITE_AUTHOR": settings.DF_SITE_AUTHOR,
        "DF_SITE_ORGANIZATION": settings.DF_SITE_ORGANIZATION,
        "DF_SITE_X_ACCOUNT": df_site_x_account,
        "DF_SITE_SOCIAL_NETWORKS": settings.DF_SITE_SOCIAL_NETWORKS.items(),
        "DF_COLOR_THEMES": settings.DF_SITE_THEMES,
        "DF_MICROSOFT_BACKGROUND_COLOR": settings.DF_MICROSOFT_BACKGROUND_COLOR,
        "DF_ANDROID_THEME_COLOR": settings.DF_ANDROID_THEME_COLOR,
        "DF_SAFARI_PINNED_COLOR": settings.DF_SAFARI_PINNED_COLOR,
        "COLOR_THEME": color_theme,
        "DF_RIBBONS": ribbons,
    }
