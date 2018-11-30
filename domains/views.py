from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import DomainForm
from .models import Domain
from aliases.models import Alias
from emaildmz.utils import get_form_errors


@method_decorator(login_required, name='dispatch')
class DomainCreate(View):
    def post(self, request, *args, **kwargs):
        # create the form with the POST data
        form = DomainForm(request.POST)

        if form.is_valid():
            # assign the domain to this user and alias, then save
            domain = form.save(commit=False)
            domain.user = self.request.user
            domain.alias = get_object_or_404(Alias, name=kwargs['alias_name'])
            domain.save()

        else:
            # process form errors
            get_form_errors(request, form)

        # whether it's a good form or not, take them to the dashboard
        return redirect(domain.alias.get_absolute_url())

@method_decorator(login_required, name='dispatch')
class DomainDelete(View):
    def get(self, request, *args, **kwargs):
        # get the domain based on the pk in the url
        domain = get_object_or_404(Domain, pk=kwargs['pk'])

        # make sure the person viewing this page is the owner
        if domain.user == request.user:

            # go to the delete confirmation page
            return render(request, 'domains/domain_delete.html', {
                'domain': domain,
            })

        # bad stuff happening here
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        # get the domain based on the name in the url
        domain = get_object_or_404(Domain, pk=kwargs['pk'])

        # store the domain's alias for the redirect later
        alias = domain.alias

        # make sure the person who submitted this is the owner
        if domain.user == request.user:

            # delete the domain
            domain.delete()

            # redirect to the dashboard
            return redirect(alias.get_absolute_url())

        # bad stuff happening here
        else:
            raise Http404
