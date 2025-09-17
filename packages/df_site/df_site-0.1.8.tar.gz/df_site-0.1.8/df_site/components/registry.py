"""Simulate a classical Django admin_site with similare URLs."""

import warnings
from collections import defaultdict
from typing import Optional, Type

from django.contrib.admin import ModelAdmin
from django.db import models


class ModelURLRegistry:
    """A registry for models and their URLs."""

    def __init__(self):
        """Initialize the registry."""
        self.all_models = defaultdict(dict)

    def register_model(self, app_label, model):
        """Register a model in the registry."""
        # Since this method is called when models are imported, it cannot
        # perform imports because of the risk of import loops. It mustn't
        # call get_app_config().
        # noinspection PyProtectedMember
        model_name = model._meta.model_name
        app_models = self.all_models[app_label]
        if model_name in app_models:
            existing = app_models[model_name]
            if model.__name__ == existing.__name__ and model.__module__ == existing.__module__:
                warnings.warn(
                    f"Model '{app_label}.{model_name}' was already registered. Reloading models is not "
                    "advised as it can lead to inconsistencies, most notably with "
                    "related models.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            else:
                msg = f"Conflicting '{model_name}' models in application '{app_label}': {existing} and {model}."
                raise RuntimeError(msg)
        app_models[model_name] = model

    def unregister_model(self, app_label, model_name):
        """Unregister a model from the registry."""
        if app_label in self.all_models:
            if model_name in self.all_models[app_label]:
                del self.all_models[app_label][model_name]
            if len(self.all_models[app_label]) == 0:
                del self.all_models[app_label]

    # noinspection PyMethodMayBeStatic
    def get_model_admin(self, model: Type[models.Model]) -> Optional[ModelAdmin]:
        """Return an empty model admin, for the sake of compatibility."""
        return None


default_registry = ModelURLRegistry()
