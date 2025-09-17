"""Override default admin filters with a custom template."""

from django.contrib.admin import AllValuesFieldListFilter as AllValuesFieldListFilterBase
from django.contrib.admin import BooleanFieldListFilter as BooleanFieldListFilterBase
from django.contrib.admin import ChoicesFieldListFilter as ChoicesFieldListFilterBase
from django.contrib.admin import DateFieldListFilter as DateFieldListFilterBase
from django.contrib.admin import EmptyFieldListFilter as EmptyFieldListFilterBase
from django.contrib.admin import FieldListFilter as FieldListFilterBase
from django.contrib.admin import RelatedFieldListFilter as RelatedFieldListFilterBase
from django.contrib.admin import RelatedOnlyFieldListFilter as RelatedOnlyFieldListFilterBase
from django.contrib.admin import SimpleListFilter as SimpleListFilterBase


class ListFilterMixin:
    """A mixin for list filters, replacing the default template."""

    template = "df_components/list_filter.html"


class SimpleListFilter(ListFilterMixin, SimpleListFilterBase):
    """A filter for simple fields."""

    pass


class FieldListFilter(ListFilterMixin, FieldListFilterBase):
    """A filter for list fields."""

    pass


class RelatedFieldListFilter(ListFilterMixin, RelatedFieldListFilterBase):
    """A filter for related fields."""

    def field_admin_ordering(self, field, request, model_admin):
        """Return the default ordering for related field, skipping the use of the admin site."""
        # noinspection PyProtectedMember
        return field.remote_field.model._meta.ordering


class BooleanFieldListFilter(ListFilterMixin, BooleanFieldListFilterBase):
    """A filter for boolean fields."""

    pass


class ChoicesFieldListFilter(ListFilterMixin, ChoicesFieldListFilterBase):
    """A filter for choice fields."""

    pass


class DateFieldListFilter(ListFilterMixin, DateFieldListFilterBase):
    """A filter for date fields."""

    pass


class AllValuesFieldListFilter(ListFilterMixin, AllValuesFieldListFilterBase):
    """A filter for all values of a field."""

    pass


class RelatedOnlyFieldListFilter(ListFilterMixin, RelatedOnlyFieldListFilterBase):
    """A filter for related fields."""

    pass


class EmptyFieldListFilter(ListFilterMixin, EmptyFieldListFilterBase):
    """A filter for empty fields."""

    pass
