"""Python functions to provide Django settings depending on other settings."""

import os
from typing import Any, Optional
from urllib.parse import urlparse


def allauth_signup_form(values: dict[str, Any]) -> Optional[str]:
    """Return the form class to use for signing up."""
    if values.get("RECAPTCHA_PRIVATE_KEY") and values.get("RECAPTCHA_PUBLIC_KEY"):
        return "df_site.users.forms.ReCaptchaForm"
    return None


allauth_signup_form.required_settings = ["RECAPTCHA_PRIVATE_KEY", "RECAPTCHA_PUBLIC_KEY"]


def are_tests_running(values: dict[str, Any]) -> bool:
    """Return True if we are running unit tests."""
    return "testserver" in values.get("ALLOWED_HOSTS", [])


are_tests_running.required_settings = ["ALLOWED_HOSTS"]


def patch_tox_environment(url_variable: str, host_variable: str, port_variable: str):
    """Patch a single URL for the workaround for https://github.com/tox-dev/tox-docker/issues/55."""
    if not all(x in os.environ for x in (host_variable, port_variable, url_variable)):
        return
    parsed_url = urlparse(os.environ[url_variable])
    if parsed_url.username or parsed_url.password:
        netloc = f"{parsed_url.username}:{parsed_url.password}@{os.environ[host_variable]}:{os.environ[port_variable]}"
    else:
        netloc = f"{os.environ[host_variable]}:{os.environ[port_variable]}"
    os.environ[url_variable] = parsed_url._replace(netloc=netloc).geturl()


def load_tox_environment():
    """Is a workaround for https://github.com/tox-dev/tox-docker/issues/55."""
    patch_tox_environment("REDIS_URL", "REDIS_HOST", "REDIS_6379_TCP_PORT")
    patch_tox_environment("DATABASE_URL", "POSTGRES_HOST", "POSTGRES_5432_TCP_PORT")
    patch_tox_environment("MAIN_STORAGE_DIR", "MINIO_HOST", "MINIO_9000_TCP_PORT")
