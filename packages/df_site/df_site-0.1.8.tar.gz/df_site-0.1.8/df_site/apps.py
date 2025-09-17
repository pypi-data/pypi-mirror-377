"""Configuration for the df_site app."""

from typing import Type

from django.apps import AppConfig
from django.db.models.signals import post_migrate, pre_save
from django.utils.translation import gettext_lazy as _


class DFSiteApp(AppConfig):
    """Configuration for the df_site app."""

    default_auto_field = "django.db.models.AutoField"
    name = "df_site"
    verbose_name = _("df_site")

    def ready(self):
        """Run code when the app is ready."""
        super().ready()
        post_migrate.connect(auto_create_site_object, sender=self)
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        pre_save.connect(create_admin_user, sender=user_model)


def create_admin_user(sender, instance, **kwargs):
    """Create an admin user if none already exists."""
    from django.contrib.auth.models import AbstractUser

    sender: Type[AbstractUser]
    instance: AbstractUser
    if hasattr(create_admin_user, "run"):
        return
    if not hasattr(instance, "is_superuser") or sender.objects.filter(is_superuser=True, is_active=True).exists():
        return
    instance.is_superuser = True
    instance.is_staff = True
    setattr(create_admin_user, "run", True)


# noinspection PyUnusedLocal
def auto_create_site_object(sender, **kwargs):
    """Create a Site object if it does not exist."""
    from django.conf import settings
    from django.contrib.sites.models import Site

    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            "domain": settings.SERVER_NAME,
            "name": settings.DF_SITE_TITLE,
        },
    )
    site.domain = settings.SERVER_NAME
    site.name = settings.DF_SITE_TITLE
    site.save()
