"""Forms for the users app."""

from django import forms
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class UserSettingsForm(forms.ModelForm):
    """Form for the user settings page."""

    class Meta:
        """Meta options for the form."""

        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "color_theme",
            "email_notifications",
            "display_online",
        ]


class ReCaptchaForm(forms.Form):
    """Form for the reCAPTCHA field."""

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=_("I'm not a robot"))

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def signup(self, request: HttpRequest, user):
        """Configure the user as required by django-allauth."""
        return user
