"""Groups all views related to the users."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import FormView

from df_site.user_settings import set_user_setting
from df_site.users.forms import UserSettingsForm


class UserSettingsView(FormView):
    """View for the user settings page."""

    template_name = "users/settings.html"
    form_class = UserSettingsForm

    def get_success_url(self):
        """Get the URL to redirect to after a successful form submission."""
        return reverse("users:settings")

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Save the form data and redirect to the success URL."""
        form.save()
        messages.success(self.request, _("Your settings have been saved."))
        return super().form_valid(form)


@never_cache
def theme_switch(request: HttpRequest) -> HttpResponse:
    """Change the color theme of the site."""
    # noinspection PyTypeChecker
    current_theme: str = request.GET.get("current", "auto")
    # noinspection PyTypeChecker
    redirect_to = sanitize_redirection(request)

    if settings.DF_SITE_THEMES:
        next_theme, __, next_icon = settings.DF_SITE_THEMES[-1]
        for theme, label, icon in settings.DF_SITE_THEMES:
            if theme == current_theme:
                break
            next_theme, next_icon = theme, icon
    else:
        next_theme, next_icon = "auto", "toggle-on"
    next_url = reverse("users:theme_switch")
    args = urlencode({"next": redirect_to, "current": next_theme})
    result = {"theme": next_theme, "icon": next_icon, "href": f"{next_url}?{args}"}
    if request.META["HTTP_ACCEPT"] == "application/json":
        response = JsonResponse(result)
    else:
        response = HttpResponseRedirect(redirect_to)
    set_user_setting("color_theme", next_theme, request=request, response=response)
    return response


def sanitize_redirection(request, param="next"):
    """Sanitize the redirection URL, only keeping allowed hosts."""
    redirect_to: str = request.GET.get(param, "/")
    if not url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_to = "/"
    return redirect_to
