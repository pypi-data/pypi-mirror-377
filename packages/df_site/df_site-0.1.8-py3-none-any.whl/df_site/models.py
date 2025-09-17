"""Models for the df_site app."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from df_site.model_fields import CKEditor5CharField, CKEditor5TextField


class AlertRibbon(models.Model):
    """Model for alert messages that are shown to users."""

    LEVELS = (
        ("info", _("Info")),
        ("success", _("Success")),
        ("warning", _("Warning")),
        ("danger", _("Danger")),
        ("primary", _("Primary")),
        ("secondary", _("Secondary")),
        ("dark", _("Dark")),
        ("light", _("Light")),
        ("tricolor", _("Tricolor")),
    )
    TOP_LEFT = 0
    BOTTOM_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_RIGHT = 3
    TOP_CENTER = 4
    BOTTOM_CENTER = 5
    POSITIONS = (
        (TOP_LEFT, _("Top left")),
        (BOTTOM_LEFT, _("Bottom left")),
        (TOP_RIGHT, _("Top right")),
        (BOTTOM_RIGHT, _("Bottom right")),
        (TOP_CENTER, _("Top center")),
        (BOTTOM_CENTER, _("Bottom center")),
    )

    color = models.CharField(max_length=10, choices=LEVELS, default="info", db_index=True, verbose_name=_("Color"))
    message = CKEditor5TextField(verbose_name=_("Message"), blank=True, default="")
    url = models.URLField(null=True, blank=True, verbose_name=_("URL"))  # noqa: DJ001
    summary = CKEditor5CharField(max_length=100, verbose_name=_("Summary"), db_index=True)
    start_date = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name=_("Start date"))
    end_date = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name=_("End date"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Is active"))
    position = models.PositiveSmallIntegerField(
        default=TOP_RIGHT, choices=POSITIONS, db_index=True, verbose_name=_("Position")
    )

    class Meta:
        """Meta options for the model."""

        ordering = ("-start_date",)
        verbose_name = _("Alert ribbon")
        verbose_name_plural = _("Alert ribbons")

    def __str__(self):
        """Return the string representation of the alert message."""
        return self.summary

    def get_absolute_url(self):
        """Return the URL for the alert message."""
        return reverse("ribbon", kwargs={"pk": self.pk})

    @property
    def html_tag(self):
        """Return the HTML tag for the alert message."""
        if self.position in (self.TOP_CENTER, self.BOTTOM_CENTER):
            return "div"
        elif self.url:
            return "a"
        return "span"

    @property
    def css_classes(self):
        """Return the CSS classes for the alert message."""
        if self.position == self.TOP_CENTER:
            classes = f"container-fluid btn btn-{self.color} "
        elif self.position == self.BOTTOM_CENTER:
            classes = f"container-fluid btn btn-{self.color} fixed-bottom "
        else:
            classes = f"alert-ribbon fixed alert-ribbon-{self.color} "
        if self.position in (self.TOP_LEFT, self.BOTTOM_LEFT):
            classes += "left-"
        elif self.position in (self.TOP_RIGHT, self.BOTTOM_RIGHT):
            classes += "right-"
        elif self.position in (self.TOP_CENTER, self.BOTTOM_CENTER):
            classes += "center-"
        if self.position in (self.TOP_LEFT, self.TOP_RIGHT, self.TOP_CENTER):
            classes += "top"
        elif self.position in (self.BOTTOM_LEFT, self.BOTTOM_RIGHT, self.BOTTOM_CENTER):
            classes += "bottom"
        return classes


class AbstractPreferences(models.Model):
    """User preferences for the df_site app."""

    COLOR_THEMES = {x[0]: x[1] for x in settings.DF_SITE_THEMES}
    color_theme = models.CharField(
        max_length=10,
        default=settings.DF_SITE_THEMES[0][0],
        db_index=True,
        choices=COLOR_THEMES,
        verbose_name=_("Color theme"),
    )
    display_online = models.BooleanField(default=False, verbose_name=_("Display online status"), db_index=True)
    email_notifications = models.BooleanField(
        default=False, verbose_name=_("Receive notifications by email"), db_index=True
    )

    class Meta:
        """Meta options for the model."""

        abstract = True


class PreferencesUser(AbstractUser, AbstractPreferences):
    """User model for the df_site app."""

    class Meta(AbstractUser.Meta):
        """Meta options for the model."""

        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        """Return the string representation of the user."""
        return super().__str__()
