"""Allow to use "python3 -m df_site" to run the manage command."""

import multiprocessing
import os
import sys
import warnings

from df_config.manage import DEFAULT_SETTINGS_MODULE, manage, set_env


def setup(module_name: str = None, settings_module=DEFAULT_SETTINGS_MODULE):
    """Setup the Django environment."""
    set_env(module_name=module_name, settings_module=settings_module)
    import django

    django.setup()
    from django.conf import settings

    return settings


def main(module_name: str = "df_site"):
    """Run the manage command."""
    if not sys.warnoptions:
        warnings.simplefilter("default")  # Change the filter in this process
        os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses
    # avoid "django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet." during parallel testing
    multiprocessing.set_start_method("fork")

    # required for parallel testing on macOS and Python 3.8+
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    manage(module_name=module_name)


if __name__ == "__main__":
    """Allow to use "python3 -m df_site"."""
    main()
