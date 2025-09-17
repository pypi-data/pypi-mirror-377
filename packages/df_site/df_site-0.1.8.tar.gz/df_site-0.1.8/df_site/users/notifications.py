"""This module contains the functions related to the notifications of the users."""

from typing import Optional, Union

from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site


# noinspection PyUnusedLocal
def email_address_on_message(user: Optional[AbstractUser], action: str, site: Site) -> Union[bool, str]:
    """Return the email address of the user if it is authenticated and if its accepts emails."""
    if user and user.is_authenticated and user.email_notifications:
        return user.email
    return False
