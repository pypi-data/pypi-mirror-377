"""Define a HTML component class, a elaborated piece of template.

A component should be instantiated once and not have any request-specific attribute.
Request-specific data should be passed as arguments to methods.
"""

from typing import List, Optional, Type

from django.db import models
from django.http import HttpRequest


class Component:
    """Base component class."""

    template_name: str = "components/base.html"

    def render(self, context, **kwargs) -> str:
        """Render the component in a HTML template.

        Context the complete template context.
        Kwargs is a dictionary of data provided to the template tag.
        """
        self.update_render_context(context, **kwargs)
        names = self.get_template_names()
        template = context.template.engine.select_template(names)
        return template.render(context)

    def get_template_names(self) -> List[str]:
        """Return a list of template names to be used for the request."""
        return [self.template_name]

    def update_render_context(self, context, **kwargs):
        """Update the context before rendering the component.

        Context the complete template context.
        Kwargs is a dictionary of data provided to the template tag.
        """
        pass


class ModelComponent(Component):
    """Base component class for model-related components."""

    template_name: Optional[str] = None

    def __init__(self, model: Type[models.Model], base_template: str):
        """Initialize the component."""
        super().__init__()
        self.model: Type[models.Model] = model
        # noinspection PyProtectedMember
        self.opts = model._meta
        self.base_template: str = base_template

    @property
    def id_prefix(self) -> str:
        """Propose a prefix for the HTML IDs linked to this component."""
        return f"{self.opts.app_label}_{self.opts.model_name}"

    # noinspection PyUnusedLocal
    def get_base_queryset(self, request: HttpRequest, **kwargs) -> models.QuerySet:
        """Return the base queryset to use for this component.

        Any extra filter based on kwargs should be applied here.
        """
        # noinspection PyProtectedMember
        return self.model._default_manager.get_queryset()

    # noinspection PyMethodMayBeStatic
    def get_empty_value_display(self) -> str:
        """Return the value to display for an empty field."""
        return "-"

    def get_template_names(self) -> List[str]:
        """Return a list of template names to be used for the request."""
        if self.template_name:
            return [self.template_name]
        return [
            f"df_components/{self.opts.app_label}/{self.opts.model_name}/{self.base_template}",
            f"df_components/{self.opts.app_label}/{self.base_template}",
            f"df_components/{self.base_template}",
        ]
