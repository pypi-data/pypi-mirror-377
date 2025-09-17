"""Check if a response from a Django view meets the expectations.

These expectations can be as low as a simple HTTP code.
"""

import json
import traceback
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional, Set, Tuple, Type, Union
from unittest import TestCase

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse


class FormHTMLParser(HTMLParser):
    """Fetch all field names in a HTML document."""

    def __init__(
        self,
        form_id: Optional[str] = None,
        convert_charrefs=True,
        ignored_fields: Optional[Set[str]] = None,
        ignored_types: Optional[Set[str]] = None,
    ):
        """Initialize the parser."""
        super().__init__(convert_charrefs=convert_charrefs)
        self.form_id = form_id
        self.form_fields: Set[str] = set()
        self.is_in_selected_form = False
        if ignored_fields is None:
            ignored_fields = {"csrfmiddlewaretoken"}
        if ignored_types is None:
            ignored_types = {"submit", "reset", "button", "image"}
        self.ignored_fields = ignored_fields
        self.ignored_types = ignored_types

    def reset(self, form_id=None):
        """Reset the parser."""
        super().reset()
        self.form_fields: Set[str] = set()
        self.is_in_selected_form = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        """Check if we are in the form and if we look at a field."""
        attrs = dict(attrs)
        if tag == "form" and (self.form_id is None or attrs.get("id") == self.form_id):
            self.is_in_selected_form = True
        if self.is_in_selected_form and tag in {"input", "select", "textarea"} and "name" in attrs:
            if attrs["name"] in self.ignored_fields:
                return
            elif tag == "input" and attrs.get("type") in self.ignored_types:
                return
            self.form_fields.add(attrs["name"])

    def handle_endtag(self, tag):
        """Check if we are still in the form."""
        if tag == "form":
            self.is_in_selected_form = False

    def error(self, message):
        """Does nothing when there is an error."""
        pass


class RequestTester:
    """Check if the response of a Django view meets the expectation."""

    def __init__(
        self,
        expected_response: Union[int, Exception, Type[Exception], HttpResponse, callable] = 200,
        method="get",
        form_data: Union[Dict[str, str], Callable] = None,
        get_data: Union[Dict[str, str], Callable] = None,
        post_data: Union[bytes, Dict[str, str], Callable] = None,
        files_data: Dict[str, SimpleUploadedFile] = None,
        raise_error: bool = False,
        reverse_kwargs: Union[Dict, Callable] = None,
        request_kwargs: Dict = None,
        view_kwargs: Union[Dict, Callable] = None,
        validators=None,
        headers: Optional[Dict[str, str]] = None,
        **response_attr,
    ):
        """Initialize the object."""
        self.method = method.lower()
        self.form_data = form_data
        self.headers = headers or {}
        self.post_data = post_data
        self.files_data = files_data or {}
        self.expected_response = expected_response
        self.raise_error = raise_error
        self.request_kwargs = request_kwargs or {}  # extra kwargs for building the HttpRequest
        self.reverse_kwargs = (
            reverse_kwargs or {}
        )  # extra kwargs provided to the callable and to the `reverse` function
        self.view_kwargs = view_kwargs or {}  # extra kwargs provided to the callabble
        self.get_data = get_data or {}  # provide the GET QueryDict of the created HttpRequest
        self.validators = validators or []  # list of callable(testCase, HttpResponse)
        self.response_attr = response_attr  # extra response attrs
        self.request = None

    @staticmethod
    def callable_value(value, test_case: TestCase, complete_url_name: str, user: AbstractUser):
        """Call the callable if possible, otherwise return the value."""
        if callable(value):
            return value(test_case, complete_url_name, user)
        return value

    # noinspection PyUnusedLocal
    def get_request_kwargs(self, test_case: TestCase, complete_url_name: str, user: AbstractUser) -> Dict:
        """Build all kwargs provided to the request factory."""
        merged_request_kwargs = {}
        merged_request_kwargs.update(self.request_kwargs)
        if self.form_data:
            merged_request_kwargs["form_data"] = self.callable_value(self.form_data, test_case, complete_url_name, user)
        if self.get_data:
            merged_request_kwargs["get_data"] = self.callable_value(self.get_data, test_case, complete_url_name, user)
        if self.post_data:
            merged_request_kwargs["post_data"] = self.callable_value(self.post_data, test_case, complete_url_name, user)
        if self.headers:
            merged_request_kwargs["headers"] = self.headers
        return merged_request_kwargs

    def get_request_method(self, test_case: TestCase, complete_url_name: str, user: AbstractUser) -> str:
        """Return the HTTP method."""
        return self.callable_value(self.method, test_case, complete_url_name, user)

    def get_view_kwargs(self, test_case: TestCase, complete_url_name: str, user: AbstractUser) -> Dict:
        """Return extra kwargs provided to the view."""
        return self.callable_value(self.view_kwargs, test_case, complete_url_name, user)

    def get_reverse_kwargs(self, test_case: TestCase, complete_url_name: str, user: AbstractUser) -> Dict:
        """Return the kwargs used for reversing the URL."""
        return self.callable_value(self.reverse_kwargs, test_case, complete_url_name, user)

    def get_http_request(self, test_case, view_name: str, reverse_kwargs: Dict, user: AbstractUser) -> HttpRequest:
        """Return the HttpRequest."""
        if view_name:
            url = reverse(view_name, kwargs=reverse_kwargs)
        else:
            url = "/unnamed/view"
        method = self.get_request_method(test_case, view_name, user)
        request_kwargs = self.get_request_kwargs(test_case, view_name, user)
        request = test_case.create_request(url, method=method, **request_kwargs)
        if self.files_data:
            request.FILES.update(self.files_data)
        request.user = user
        return request

    def evaluate(
        self,
        test_case,
        view_name: str,
        view: callable,
        reverse_kwargs: Dict,
        view_kwargs: Dict,
        user: AbstractUser,
    ) -> Optional[Exception]:
        """Evaluate a single view with the provided reverse kwargs and view kwargs.

        :param test_case: the test case evaluating this function (maybe some attributes are required)
        :param view_name: the name of the tested view
        :param view: the tested view itself
        :param reverse_kwargs: kwargs used for the `reverse` function (updated by `get_reverse_kwargs`)
        :param view_kwargs: extra args passed to the view (updated by `get_view_kwargs`)
        :param user: the tested permission set
        """
        merged_reverse_kwargs = {}
        merged_reverse_kwargs.update(reverse_kwargs)
        merged_reverse_kwargs.update(self.get_reverse_kwargs(test_case, view_name, user))

        request = self.get_http_request(test_case, view_name, merged_reverse_kwargs, user)
        self.request = request

        merged_view_kwargs = merged_reverse_kwargs
        merged_view_kwargs.update(view_kwargs)
        merged_view_kwargs.update(self.get_view_kwargs(test_case, view_name, user))
        if self.raise_error:
            self.check_response(test_case, request, view, merged_view_kwargs, user)
        else:
            try:
                self.check_response(test_case, request, view, merged_view_kwargs, user)
            except Exception as e:
                if not isinstance(e, PermissionDenied) and not isinstance(e, Http404):
                    traceback.print_exc()
                return e

    def check_response(
        self,
        test_case: TestCase,
        request: HttpRequest,
        view: callable,
        view_kwargs: Dict,
        user: AbstractUser,
    ):
        """Check if the response meets the expectation."""
        expected_response = self.expected_response
        # noinspection PyUnusedLocal
        user = user
        if isinstance(expected_response, type) and issubclass(expected_response, Exception):
            test_case.assertRaises(expected_response, lambda: view(request, **view_kwargs))
            return
        http_response = view(request, **view_kwargs)
        if isinstance(http_response, TemplateResponse):
            http_response.render()
        for validator in self.validators:
            validator(test_case, http_response)
        if isinstance(expected_response, int):
            if expected_response != http_response.status_code:
                # do not use test_case.assertEqual to have a more explicit error
                msg = f"HTTP {http_response.status_code} (while expecting {expected_response})"
                msg += self.get_description(request)
                raise AssertionError(msg)
        elif isinstance(expected_response, HttpResponse):
            if expected_response.status_code != http_response.status_code:
                # do not use test_case.assertEqual to have a more explicit error
                msg = f"HTTP {http_response.status_code} (while expecting {expected_response.status_code})"
                msg += self.get_description(request)
                raise AssertionError(msg)
            test_case.assertIsInstance(http_response, expected_response.__class__)
        elif callable(expected_response):
            expected_response(test_case, http_response)
        else:
            raise ValueError(f"unknown type of expected response: {expected_response!r}")
        for attr_name, attr_value in self.response_attr.items():
            if isinstance(attr_value, type):
                test_case.assertIsInstance(attr_value, getattr(http_response, attr_name))
            else:
                test_case.assertEqual(attr_value, getattr(http_response, attr_name))

    def get_description(self, request: HttpRequest) -> str:
        """Return a string representation of a RequestTester."""
        msg = f" url = {request.path}"
        if self.method != "get":
            msg += f" method={self.method}"
        if self.headers:
            msg += f" headers={self.headers}"
        if self.post_data:
            post_data = str(self.post_data)[:30]
            msg += f" post_data={post_data}"
        if self.form_data or self.get_data:
            post_data = str(self.form_data)[:30]
            msg += f" form_data={post_data}"
        if self.get_data:
            post_data = str(self.get_data)[:30]
            msg += f" get_data={post_data}"
        return msg


class HTMLFormRequestTester(RequestTester):
    """Validate a form in the HTML response, for example to check if required fields are present."""

    def __init__(
        self,
        required_fields: Set[str],
        *args,
        form_id: Optional[str] = None,
        ignored_fields: Optional[Set[str]] = None,
        ignored_types: Optional[Set[str]] = None,
        **kwargs,
    ):
        """Initialize the object with expected values."""
        self.required_fields = required_fields
        kwargs.setdefault("validators", [])
        kwargs["validators"].append(self.check_required_fields)
        self.form_id = form_id
        self.ignored_fields = ignored_fields
        self.ignored_types = ignored_types
        super().__init__(*args, **kwargs)

    def check_required_fields(self, test_case: TestCase, response: HttpResponse):
        """Check if the response contains the expected form values."""
        parser = FormHTMLParser(
            form_id=self.form_id,
            ignored_types=self.ignored_types,
            ignored_fields=self.ignored_fields,
        )
        parser.feed(response.content.decode())
        test_case.assertEqual(self.required_fields, parser.form_fields)


class JsonValidator:
    """Validate a JSONResponse."""

    def __init__(self, value):
        """Initialize the object with the expected JSON."""
        self.value = value

    def __call__(self, test_case: TestCase, response: JsonResponse):
        """Check the content of a JsonResponse."""
        content = json.loads(response.content)
        if self.value != content:
            print(content)
        test_case.assertEqual(self.value, content)
