"""Define custom model fields with the CKEditor5 widget."""

from django.db import models

from df_site import form_fields


class CKEditor5TextField(models.TextField):
    """Use a CKEditor5 widget for a TextField."""

    def formfield(self, **kwargs):
        """Replace the default widget with a CKEditor5 widget."""
        defaults = {"form_class": form_fields.CKEditor5Field}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class CKEditor5CharField(models.CharField):
    """Use a CKEditor5 widget for a CharField."""

    def formfield(self, **kwargs):
        """Replace the default widget with a CKEditor5 widget."""
        defaults = {"form_class": form_fields.InlineCKEditor5Field}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class CKEditor5LinkCharField(models.CharField):
    """Use a CKEditor5 widget for a CharField, allowing to write URLs."""

    def formfield(self, **kwargs):
        """Replace the default widget with a CKEditor5 widget."""
        defaults = {"form_class": form_fields.InlineLinkCKEditor5Field}
        defaults.update(kwargs)
        return super().formfield(**defaults)
