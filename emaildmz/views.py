from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from allauth.account import views

from aliases.forms import AliasForm
from aliases.models import Alias
from aliases.utils import get_alias_recipients, get_user_aliases
from filters.forms import FilterForm
from filters.utils import get_alias_filters, get_user_filters
from recipients.forms import RecipientForm
from recipients.models import Recipient

@login_required
def dashboard_view(request, alias_name=None):
    aliases = get_user_aliases(request.user)

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
            filters = None

    if active_alias:
        # if there's an active alias, make sure the person viewing this is the owner
        if not active_alias.user == request.user:
            raise Http404

        # at this point, we've made sure this user is the owner
        else:
            # get the active alias's recipients
            recipients = get_alias_recipients(active_alias)

            # get the active alias's filters
            filters = get_alias_filters(active_alias)

    # no active alias, so no recipients to get
    else:
        recipients = None

    return render(request, 'dashboard.html', {
        'active_alias': active_alias,
        'alias_form': AliasForm(),
        'aliases': aliases,
        'filter_form': FilterForm(),
        'filters': filters,
        'recipient_form': RecipientForm(),
        'recipients': recipients,
    })

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
