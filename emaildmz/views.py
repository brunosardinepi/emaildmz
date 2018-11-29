from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from allauth.account import views

from aliases.forms import AliasForm
from aliases.utils import get_user_aliases, get_user_forwardingemails
from domains.utils import get_user_domains


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, *args, **kwargs):
        # need aliases, forwarding emails, and domains
        context = super().get_context_data(**kwargs)
        context['alias_form'] = AliasForm()
        context['aliases'] = get_user_aliases(self.request.user)
        context['domains'] = get_user_domains(self.request.user)
        context['forwardingemails'] = get_user_forwardingemails(self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class HomeView(TemplateView):
    template_name = 'home.html'

class LoginView(views.LoginView):
    template_name = 'login.html'

class SignupView(views.SignupView):
    template_name = 'signup.html'
