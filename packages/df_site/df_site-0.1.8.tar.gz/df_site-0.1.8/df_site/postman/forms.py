"""Forms for the Postman application."""

from django import forms
from django.utils.translation import gettext_lazy as _
from postman.forms import AnonymousWriteForm, FullReplyForm, QuickReplyForm, WriteForm

from df_site.form_fields import CKEditor5Field


class CKEditor5Form(forms.Form):
    """Form with a CKEditor 5 widget."""

    body = CKEditor5Field(label=_("body"), required=True, config_name="default")
    subject = CKEditor5Field(label=_("subject"), required=True, config_name="inline")


class HTMLWriteForm(CKEditor5Form, WriteForm):
    """Form used by authenticated users."""

    pass


class HTMLAnonymousWriteForm(CKEditor5Form, AnonymousWriteForm):
    """Form used by anonymous users."""

    pass


class HTMLFullReplyForm(CKEditor5Form, FullReplyForm):
    """Form for complete Postman replies."""

    pass


class HTMLQuickReplyForm(CKEditor5Form, QuickReplyForm):
    """Form for postman quick replies."""

    pass
