"""Component and generic View for displaying the details of a model instance."""

from typing import Dict, List, Optional, Type, Union

from df_websockets.tasks import set_websocket_topics
from django import forms
from django.contrib.admin import helpers
from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields_for_model
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView

from df_site.components.base import ModelComponent


class ModelDetailComponent(ModelComponent):
    """A component that displays the details of a model instance."""

    model: Type[models.Model]

    def __init__(
        self,
        model: Type[models.Model],
        base_template: str = "detail.html",
        inlines: List = None,
        fields=None,
        exclude=None,
        fieldsets=None,
        filter_vertical=(),
        filter_horizontal=(),
    ):
        """Initialize the component."""
        super().__init__(model, base_template)
        self.inlines = inlines or []
        self.fields = fields
        self.exclude = exclude
        self.fieldsets = fieldsets
        self.filter_vertical = filter_vertical
        self.filter_horizontal = filter_horizontal
        self.opts = model._meta

    def get_queryset(self, request):
        """Return a QuerySet of all model instances that can be viewed."""
        # noinspection PyProtectedMember
        return self.model._default_manager.get_queryset()

    def get_fields(self, request, obj=None):
        """Return the list of selected fields."""
        if self.fields:
            return self.fields
        # _get_form_for_get_fields() is implemented in subclasses.
        fields = fields_for_model(self.model)
        return [*fields]

    def get_fieldsets(self, request, obj=None):
        """Return the specified fieldsets."""
        if self.fieldsets:
            return self.fieldsets
        return [(None, {"fields": self.get_fields(request, obj)})]

    def get_inlines(self, request, obj):
        """Hook for specifying custom inlines."""
        return self.inlines

    def get_object(self, request, object_id, from_field=None):
        """Return an instance matching the field and value provided.

        The primary key is used if no field is provided. Return ``None`` if no match is
        found or the object_id fails validation.
        """
        queryset = self.get_queryset(request)
        model = queryset.model
        field = self.opts.pk if from_field is None else self.opts.get_field(from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def update_render_context(self, context, **kwargs):
        """Update the context before rendering the component.

        The displayed object can be specified either in the context as "object",
         in the kwargs as "obj" or its ID as "object_id" in kwargs.
        """
        request = context["request"]
        if "object" in context:
            obj = context["object"]
        elif "obj" in kwargs:
            obj = kwargs["obj"]
        else:
            object_id = kwargs.get("object_id")
            from_field = kwargs.get("from_field")
            obj = self.get_object(request, object_id=object_id, from_field=from_field)
        fieldsets = self.get_fieldsets(request, obj)
        readonly_fields = flatten_fieldsets(fieldsets)

        class AdminForm(forms.ModelForm):
            class Meta:
                model = self.model
                fields = []

        form = AdminForm(instance=obj)
        admin_form = helpers.AdminForm(
            form,
            list(fieldsets),
            {},
            readonly_fields=readonly_fields,
            model_admin=self,
        )
        context["adminform"] = admin_form


class ModelDetailView(DetailView):
    """A view that displays the details of a model instance."""

    component: ModelDetailComponent
    model: Type[models.Model]
    component_template: str = "detail.html"
    inlines: List = None
    fields = None
    exclude = None
    fieldsets = None
    filter_vertical = ()
    filter_horizontal = ()

    @classmethod
    def as_view(cls, **initkwargs):
        """Main entry point for a request-response process."""
        cls.component = ModelDetailComponent(
            model=cls.model,
            base_template=cls.component_template,
            inlines=cls.inlines,
            fields=cls.fields,
            exclude=cls.exclude,
            fieldsets=cls.fieldsets,
            filter_vertical=cls.filter_vertical,
            filter_horizontal=cls.filter_horizontal,
        )
        return super().as_view(**initkwargs)

    def get_template_names(self):
        """Return a list of template names to be used for the request."""
        if self.template_name:
            return [self.template_name]
        return [
            f"df_site/{self.component.opts.app_label}/{self.component.opts.model_name}/detail.html",
            f"df_site/{self.component.opts.app_label}/detail.html",
            "df_site/detail.html",
        ]

    def get_breadcrumb(self) -> List[Dict[str, Union[str, bool]]]:
        """Return the breadcrumb for the view.

        The breadcrumb is a list of dictionaries with the following keys:
        * `link`: URL to link to
        * `title`: Text to display
        * `active`: boolean, element is active, meaning that the link is not displayed
        """
        return [
            {"link": reverse("index"), "title": _("Home"), "active": False},
            {"link": None, "title": str(self.object), "active": True},
        ]

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        context["detail_component"] = self.component
        context["detail_breadcrumb"] = self.get_breadcrumb()
        context["PAGE_TITLE"] = self.get_page_title()
        context["PAGE_DESCRIPTION"] = self.get_page_description()
        context["PAGE_URL"] = self.get_page_url(context)
        set_websocket_topics(self.request, self.object)
        return context

    def get_page_url(self, context) -> Optional[str]:
        """Return the URL of the current page."""
        if hasattr(self.object, "get_absolute_url"):
            return self.object.get_absolute_url()

    def get_page_title(self) -> Optional[str]:
        """Return the title of the current page."""
        return str(self.object)

    def get_page_description(self) -> Optional[str]:
        """Return the description of the current page."""
        # noinspection PyProtectedMember
        return self.object._meta.verbose_name
