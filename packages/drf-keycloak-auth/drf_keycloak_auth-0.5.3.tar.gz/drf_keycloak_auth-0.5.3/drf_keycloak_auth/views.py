import logging
from urllib.parse import urljoin, urlparse
from django.contrib.auth import views
from django.http import HttpResponseRedirect, QueryDict
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from drf_keycloak_auth.keycloak import get_keycloak_openid

log = logging.getLogger(__name__)


class LoginView(views.LoginView):
    redirect_authenticated_user = True

    def get_keycloak_auth_url(self, request):
        keycloak_openid = get_keycloak_openid(host=request.get_host())

        # Redirect back to this app
        absolute_uri = request.build_absolute_uri()
        redirect_uri = urljoin(absolute_uri, self.get_success_url())

        # Get the Keycloak auth url
        auth_url = keycloak_openid.auth_url(redirect_uri=redirect_uri)
        log.info(f"get_keycloak_auth_url | redirecting to Keycloak: {auth_url}")
        return auth_url

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)

        # Keycloak login
        if not self.request.user or not self.request.user.is_authenticated:
            redirect_to = self.get_keycloak_auth_url(request)
            return HttpResponseRedirect(redirect_to)

        return super().dispatch(request, *args, **kwargs)


class LogoutView(views.LogoutView):
    pass
