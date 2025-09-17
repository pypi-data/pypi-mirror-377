"""A generic class testing several views with different users.

The expected response can by defined by the response code, a HttpResponse, an exception or a callable.
In these case, a RequestTester will be built with this value as first argument.
Otherwise, you can also provide a RequestTester (especially to provide GET or POST arguments).
"""

import logging
from typing import Dict, List, Optional, Tuple, Type, TypeAlias, Union
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import site as default_site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404, HttpResponse, SimpleCookie
from django.middleware.csrf import get_token
from django.test import RequestFactory, TestCase
from django.urls import URLPattern
from django.urls.resolvers import RoutePattern
from django.utils.encoding import iri_to_uri

from df_site.testing.requests import RequestTester

logger = logging.getLogger(__name__)
ExpectedResponse: TypeAlias = Union[int, Exception, Type[Exception], HttpResponse, callable, RequestTester]
ExpectedResponses = Union[List[ExpectedResponse], ExpectedResponse]


class TestMultipleViews(TestCase):
    """Define some methods for testing a set of views with different users (identified by its username).

    `expected_responses` is a dict such that:
    - the key is the view name
    - the value is a dict such that:
        - the key is a USER_KEY (can be anything, like its privilege level)
        - the value is any of:
            - an integer (the expected HTTP status code — then this is the only checked thing)
            - an exception (only the type of the raised exception is checked)
            - a HttpResponse (only status_codes are checked)
            - a callable that will be given the TestCase and the HttpResponse as arguments
            - a RequestTester to deeply customize the test (including the request args/kwargs)
            - a list of any of the previous values

    You must override `get_user_keys` to provide a list of values to create different users.
        (`str(value)` is used to get the username)
    Your test_* methods must call
        check_url_patterns(url_patterns, common_kwargs, expected_responses, display_prefix=display_prefix)
    """

    views_test_counter = 0
    call_test_counter = 0

    @classmethod
    def setUpClass(cls):
        """Create some users and a request factory for testing."""
        super().setUpClass()
        # Every test needs access to the request factory.
        cls.request_factory = RequestFactory()
        cls.created_users: List[AbstractUser] = cls.create_users()

    def setUp(self):
        """Counts the number of run tests."""
        TestMultipleViews.call_test_counter += 1
        return super().setUp()

    @classmethod
    def get_users(cls) -> List[AbstractUser]:
        """Teturn a list of values to identify different users.

        The special value `None` is dedicated to AnonymousUser.
        """
        return cls.created_users

    @classmethod
    def create_users(cls):
        """Create some users for testing."""
        return [
            AnonymousUser(),
            cls.create_user("staff", is_staff=True),
            cls.create_user("admin", is_staff=True, is_superuser=True),
        ]

    @classmethod
    def create_user(cls, name, is_active=True, **kwargs):
        """Create a user with the provided name."""
        user = get_user_model().objects.filter(username=name).first()
        if user is not None:
            return user
        user_kwargs = {
            "email": f"{name}@test.com",
            "is_active": is_active,
        }
        user_kwargs.update(kwargs)
        return get_user_model().objects.create_user(username=name, **user_kwargs)

    def create_request(
        self,
        url,
        *args,
        method=None,
        user=None,
        form_data=None,
        get_data=None,
        post_data=None,
        **kwargs,
    ):
        """Return a request object for the provided URL."""
        if form_data:
            kwargs["data"] = urlencode(form_data)
            kwargs["content_type"] = "application/x-www-form-urlencoded"
        if method:
            method = method.lower()
        if method and method in ("get", "head") and get_data:
            kwargs["data"] = get_data
        elif get_data:
            kwargs["QUERY_STRING"] = urlencode(get_data, doseq=True)
        if post_data:
            kwargs["data"] = post_data
            method = method or "post"
            request = self.request_factory.generic(method.upper(), url, *args, **kwargs)
        else:
            method = method or "get"
            request = getattr(self.request_factory, method)(url, *args, **kwargs)
        request.user = user or AnonymousUser()
        request.cookies = SimpleCookie()
        setattr(request, "_dont_enforce_csrf_checks", True)
        request.cookies["csrftoken"] = get_token(request)

        def get_response():
            pass

        SessionMiddleware(get_response).process_request(request)
        MessageMiddleware(get_response).process_request(request)
        return request

    def check_url_patterns(
        self,
        url_patterns: List[Tuple[str, URLPattern]],
        common_kwargs: Dict[str, str],
        expected_responses: Dict[str, Dict[Optional[str], ExpectedResponses]],
        display_prefix: str = "",
    ):
        """Check all provided URL patterns.

        :param url_patterns: list of ("namespace:", URLPattern)  (leave "" if no namespace)
        :param common_kwargs: kwargs common to all URL patterns
            (use `expected_responses` to provided kwargs specific to a URL pattern)
        :param expected_responses:
        :param display_prefix: prefix added to displayed error messages
        :return:
        """
        failures = []  # list of (url_pattern, ps, exception)
        for namespace, url_pattern in url_patterns:
            if url_pattern.name:
                view_name = f"{namespace}{url_pattern.name}"
            else:
                view_name = None
            url_name = self.format_url_pattern(url_pattern)
            view = url_pattern.callback
            provided_view_kwargs = url_pattern.default_args
            # "kwargs" argument provided to path()
            if isinstance(url_pattern.pattern, RoutePattern):
                arg_names = list(url_pattern.pattern.converters.keys())
            else:
                arg_names = list(url_pattern.pattern.regex.groupindex)
            reverse_kwargs = {k: common_kwargs[k] for k in arg_names if k in common_kwargs}
            for user in self.get_users():
                username = None if user.is_anonymous else user.username
                request_testers_: ExpectedResponses = expected_responses.get(url_name, {}).get(username, Http404)
                if not isinstance(request_testers_, list):
                    request_testers: List[ExpectedResponse] = [request_testers_]
                else:
                    request_testers: List[ExpectedResponse] = request_testers_
                for request_tester in request_testers:
                    if not isinstance(request_tester, RequestTester):
                        request_tester = RequestTester(request_tester)
                    # actual view kwargs are the kwargs provided in the get_urls()
                    self.__class__.views_test_counter += 1
                    exc = request_tester.evaluate(
                        self,
                        view_name,
                        view,
                        reverse_kwargs,
                        provided_view_kwargs,
                        user,
                    )
                    if exc is not None:
                        failed_url = request_tester.request.path + (
                            "?" + iri_to_uri(request_tester.request.META.get("QUERY_STRING", ""))
                            if request_tester.request.META.get("QUERY_STRING", "")
                            else ""
                        )
                        failure = (
                            url_pattern,
                            username,
                            exc,
                            failed_url,
                        )
                        failures.append(failure)
        for url_pattern, username, e, url in failures:
            pattern = self.format_url_pattern(url_pattern)
            if username is None:
                username = "AnonymousUser"
            else:
                username = f"user {username}"
            base_url = settings.SERVER_BASE_URL[:-1]
            msg = f"{display_prefix}Exception in {pattern} with {username}: {e} ({base_url}{url})."
            print(msg)
        self.assertEqual(0, len(failures))

    @staticmethod
    def format_url_pattern(url_pattern) -> str:
        """Return a string representation of the provided URL pattern."""
        if url_pattern.name:
            return url_pattern.name
        if isinstance(url_pattern.pattern, RoutePattern):
            return url_pattern.pattern._route
        return url_pattern.pattern._regex


class TestModelAdmin(TestMultipleViews):
    """Define some methods for testing *all* views defined in the get_urls() of a ModelAdmin.

     Each view is tested with different users.
    . A RequestTester define more precisely how to test a given view with a given user.

    Many of these views require some kwargs for the `reverse` function, but most of them have always the same meaning.
    So, we always reuse the same kwargs for all views (but we can override them in a RequestTester).

    `expected_responses` is a dict such that:
    - the key is the view name
    - the value is a dict such that:
        - the key is a username (or None for AnonymousUser)
        - the value is any of:
            - an integer (the expected HTTP status code — then this is the only checked thing)
            - an exception (only the type of the raised exception is checked)
            - a HttpResponse (only status_codes are checked)
            - a callable that will be given the TestCase and the HttpResponse as arguments
            - a RequestTester to deeply customize the test (including the request args/kwargs)
            - a list of any of the previous values

    """

    checked_model_admins = set()
    placeholders = "%(app_label)s_%(model_name)s_"
    expected_responses: Dict[str, Dict[Optional[str], ExpectedResponses]] = {
        f"{placeholders}changelist": {
            None: 302,
            "staff": PermissionDenied,
            "admin": 200,
        },
        f"{placeholders}add": {
            None: 302,
            "staff": PermissionDenied,
            "admin": 200,
        },
        f"{placeholders}history": {
            None: 302,
            "staff": PermissionDenied,
            "admin": 200,
        },
        f"{placeholders}delete": {
            None: 302,
            "staff": PermissionDenied,
            "admin": 200,
        },
        f"{placeholders}change": {
            None: 302,
            "staff": PermissionDenied,
            "admin": 200,
        },
        "<path:object_id>/": {
            None: 302,
            "staff": 302,
            "admin": 302,
        },
    }

    # expected_responses["view_name"]["staff"] = 200
    # %(app_label)s and %(model_name)s can
    # be used in the view names to avoid repeating the same values.
    def check_model_admin(
        self,
        model_admin: Union[Type[admin.ModelAdmin], Type[models.Model]],
        common_kwargs: Dict[str, str],
        display_prefix: str = "",
        expected_responses: Dict[str, Dict[Optional[str], ExpectedResponses]] = None,
    ):
        """Check all admin views.

        :param model_admin: the models.Model or admin.ModelAdmin to check
        :param common_kwargs: dict of values for reversing URLs
        :param display_prefix: prefix to display in front of each error
        :param expected_responses: extra responses, only for this ModelAdmin
            (same format as self.expected_responses)
        :return:
        """
        if isinstance(model_admin, type) and issubclass(model_admin, models.Model):
            model_admin = default_site.get_model_admin(model_admin)

        TestModelAdmin.checked_model_admins.add(model_admin)
        base_expected_responses = self.get_expected_responses(model_admin, raw_expected_responses=expected_responses)
        # with app_label="app", model_name="model", if we have both
        #   "%(app_label)s_%(model_name)s_viewname" and "app_model_viewname" keys  in raw_expected_responses
        #   we do not want to override the initial values.
        url_patterns = self.get_admin_urls(model_admin)
        self.check_url_patterns(
            url_patterns,
            common_kwargs,
            base_expected_responses,
            display_prefix=display_prefix,
        )

    def get_expected_responses(
        self,
        model_admin: admin.ModelAdmin,
        raw_expected_responses: Dict[str, Dict[Optional[str], ExpectedResponses]] = None,
    ) -> Dict[str, Dict[Optional[str], ExpectedResponses]]:
        """Return the expected responses for this model_admin.

        Replace %(app_label)s and %(model_name)s placeholders in the view names and use
        them when these view names are missing from the expected_responses.
        """
        base_expected_responses = {}
        base_expected_responses.update(self.expected_responses)
        if raw_expected_responses is not None:
            base_expected_responses.update(raw_expected_responses)

        opts = {
            "app_label": model_admin.model._meta.app_label,
            "model_name": model_admin.model._meta.model_name,
        }
        expected_responses = {url_name % opts: v for (url_name, v) in base_expected_responses.items() if url_name}
        expected_responses.update(base_expected_responses)
        return expected_responses

    # noinspection PyMethodMayBeStatic
    def get_admin_urls(self, model_admin: admin.ModelAdmin) -> List[Tuple[str, URLPattern]]:
        """Return the list of all URLs in this model_admin."""
        return [("admin:", x) for x in model_admin.get_urls()]


class TestModel(TestModelAdmin):
    """Define some methods for testing all views defined in the get_urls() of a ModelAdmin."""

    def get_object(self):
        """Return an object of the model to test."""
        raise NotImplementedError("You must override this method to return an object of the model to test.")

    def test_model_admin(self):
        """Test all views of the model admin correspoding to the provided object."""
        try:
            obj = self.get_object()
        except NotImplementedError as e:
            self.skipTest(str(e))
        if obj._state.adding:
            obj.save()
        common_kwargs = self.get_common_kwargs_for_object(obj)
        self.check_model_admin(obj.__class__, common_kwargs=common_kwargs, display_prefix="")

    def get_common_kwargs_for_object(self, obj) -> Dict[str, str]:
        """Return the common kwargs for all views of the provided object."""
        return {"object_id": str(obj.pk)}
