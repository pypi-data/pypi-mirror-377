"""URLs for customized views (mainly customized forms)."""

from django.conf import settings
from django.urls import include, re_path
from postman import api_urls
from postman.views import (
    ArchivesView,
    ArchiveView,
    ConversationView,
    DeleteView,
    InboxView,
    IndexView,
    MarkReadView,
    MarkUnreadView,
    MessageView,
    ReplyView,
    SentView,
    TrashView,
    UndeleteView,
    WriteView,
)

from df_site.postman.forms import HTMLAnonymousWriteForm, HTMLFullReplyForm, HTMLQuickReplyForm, HTMLWriteForm
from df_site.postman.views import MessageUpdateView

if settings.POSTMAN_I18N_URLS:
    from django.utils.translation import pgettext_lazy
else:

    def pgettext_lazy(context: str, message: str):
        """Does nothing when POSTMAN_I18N_URLS is off."""
        return message


app_name = "postman"
urlpatterns = [
    # Translators: keep consistency of the <option> parameter with the translation for 'm'
    re_path(pgettext_lazy("postman_url", r"^inbox/(?:(?P<option>m)/)?$"), InboxView.as_view(), name="inbox"),
    # Translators: keep consistency of the <option> parameter with the translation for 'm'
    re_path(pgettext_lazy("postman_url", r"^sent/(?:(?P<option>m)/)?$"), SentView.as_view(), name="sent"),
    # Translators: keep consistency of the <option> parameter with the translation for 'm'
    re_path(pgettext_lazy("postman_url", r"^archives/(?:(?P<option>m)/)?$"), ArchivesView.as_view(), name="archives"),
    # Translators: keep consistency of the <option> parameter with the translation for 'm'
    re_path(pgettext_lazy("postman_url", r"^trash/(?:(?P<option>m)/)?$"), TrashView.as_view(), name="trash"),
    re_path(
        pgettext_lazy("postman_url", r"^write/(?:(?P<recipients>[^/#]+)/)?$"),
        WriteView.as_view(form_classes=(HTMLWriteForm, HTMLAnonymousWriteForm)),
        name="write",
    ),
    re_path(
        pgettext_lazy("postman_url", r"^reply/(?P<message_id>[\d]+)/$"),
        ReplyView.as_view(form_class=HTMLFullReplyForm),
        name="reply",
    ),
    re_path(
        pgettext_lazy("postman_url", r"^view/(?P<message_id>[\d]+)/$"),
        MessageView.as_view(form_class=HTMLQuickReplyForm),
        name="view",
    ),
    # Translators: 't' stands for 'thread'
    re_path(
        pgettext_lazy("postman_url", r"^view/t/(?P<thread_id>[\d]+)/$"),
        ConversationView.as_view(form_class=HTMLQuickReplyForm),
        name="view_conversation",
    ),
    re_path(pgettext_lazy("postman_url", r"^archive/$"), ArchiveView.as_view(), name="archive"),
    re_path(pgettext_lazy("postman_url", r"^delete/$"), DeleteView.as_view(), name="delete"),
    re_path(pgettext_lazy("postman_url", r"^undelete/$"), UndeleteView.as_view(), name="undelete"),
    re_path(pgettext_lazy("postman_url", r"^mark-read/$"), MarkReadView.as_view(), name="mark-read"),
    re_path(pgettext_lazy("postman_url", r"^mark-unread/$"), MarkUnreadView.as_view(), name="mark-unread"),
    # this view is not a part of the original postman views
    re_path(pgettext_lazy("postman_url", r"^mark-message/$"), MessageUpdateView.as_view(), name="update-message"),
    re_path(r"^$", IndexView.as_view()),
    re_path(pgettext_lazy("postman_url", r"^api/"), include(api_urls, namespace="api")),
]
