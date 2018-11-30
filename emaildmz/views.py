from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from allauth.account import views

from aliases.forms import AliasForm, ForwardingEmailForm
from aliases.models import Alias
from aliases.utils import (get_alias_forwardingemails,
                           get_user_aliases,
                           get_user_forwardingemails)
from domains.utils import get_user_domains


@login_required
def dashboard_view(request, alias_name=None):
    alias_form = AliasForm()
    aliases = get_user_aliases(request.user)
    domains = get_user_domains(request.user)
#    forwardingemails = get_user_forwardingemails(request.user)
    forwardingemail_form = ForwardingEmailForm()

    if alias_name:
        # find the alias object
        # and set it to the active alias
        active_alias = get_object_or_404(Alias, name=alias_name)

    else:
        # if this user has aliases,
        # find the first alphabetical alias object
        # and set it to the active alias
        if aliases:
            active_alias = Alias.objects.filter(user=request.user).order_by('name')[0]

        # otherwise, there is no active alias
        else:
            active_alias = None

    if active_alias:
        # if there's an active alias, make sure the person viewing this is the owner
        if not active_alias.user == request.user:
            raise Http404

        # get the active alias's forwardingemails
        # note: we've already made sure this user is the owner
        else:
            forwardingemails = get_alias_forwardingemails(active_alias)

    # no active alias, so no forwardingemails to get
    else:
        forwardingemails = None


    return render(request, 'dashboard.html', {
        'active_alias': active_alias,
        'alias_form': alias_form,
        'aliases': aliases,
        'domains': domains,
        'forwardingemails': forwardingemails,
        'forwardingemail_form': forwardingemail_form,
    })

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alias_form'] = AliasForm()
        context['aliases'] = get_user_aliases(self.request.user)
        context['domains'] = get_user_domains(self.request.user)
        context['forwardingemails'] = get_user_forwardingemails(self.request.user)
        context['forwardingemail_form'] = ForwardingEmailForm()

        if kwargs['alias_name']:
            print("there is a alias_name in the url")
        else:
            print("no alias_name in url")

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
