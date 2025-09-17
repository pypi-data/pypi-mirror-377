"""Set default topics for websockets."""

from df_websockets.tasks import set_websocket_topics
from django.http import HttpRequest, HttpResponse


def websocket_middleware(get_response):
    """Set default topics for websockets, when not set yet."""

    def middleware(request: HttpRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response: HttpResponse = get_response(request)
        # noinspection PyUnresolvedReferences
        if hasattr(request, "has_websocket_topics") and not request.has_websocket_topics:
            set_websocket_topics(request)
        return response

    return middleware
