"""Customized postman views."""

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.generic import View
from postman.models import Message
from postman.views import UpdateDualMixin


class MessageUpdateView(UpdateDualMixin, View):
    """View for updating messages or conversations.

    This single view replaces the following views: `ArchiveView`, `DeleteView`,
    `UndeleteView`, 'MarkReadView', 'MarkUnreadView'.
    This is required to avoid the onclick attribute in the template (forbidden by CSP).
    """

    @property
    def selected_action(self):
        """Get the action to perform on the selected messages or conversations."""
        action = self.request.POST.get("action")
        if action not in {"delete", "archive", "undelete", "read", "unread"}:
            raise PermissionDenied
        return action

    def _action(self, user: AbstractBaseUser, filter_: Q):
        """Perform the action on the selected messages or conversations."""
        if self.selected_action in {"read", "unread"}:
            Message.objects.as_recipient(user, filter_).filter(
                **{f"{self.field_bit}__isnull": bool(self.field_value)}
            ).update(**{self.field_bit: self.field_value})
        else:
            super()._action(user, filter_)
        # an empty set cannot be estimated as an error, it may be just a badly chosen selection

    @property
    def field_bit(self):
        """Get the field to update."""
        return {
            "delete": "deleted_at",
            "archive": "archived",
            "undelete": "deleted_at",
            "read": "read_at",
            "unread": "read_at",
        }[self.selected_action]

    @property
    def success_msg(self):
        """Get the success message to display."""
        return {
            "delete": _("Messages or conversations successfully deleted."),
            "archive": _("Messages or conversations successfully archived."),
            "undelete": _("Messages or conversations successfully recovered."),
            "read": _("Messages or conversations successfully marked as read."),
            "unread": _("Messages or conversations successfully marked as unread."),
        }[self.selected_action]

    @property
    def field_value(self):
        """Get the value to set the field to."""
        n = now()
        return {"delete": n, "archive": True, "undelete": None, "read": n, "unread": None}[self.selected_action]
