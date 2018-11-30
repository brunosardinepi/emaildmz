from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import AliasForm
from .models import Alias
from .utils import get_user_aliases
from emaildmz.utils import get_form_errors


@method_decorator(login_required, name='dispatch')
class AliasCreate(View):
    def post(self, request, *args, **kwargs):
        # create the form with the POST data
        form = AliasForm(request.POST)

        if form.is_valid():
            # assign the alias to this user, then save
            alias = form.save(commit=False)
            alias.user = self.request.user
            alias.save()

        else:
            # process form errors
            get_form_errors(request, form)

        # whether it's a good form or not, take them to the dashboard
        return redirect(alias.get_absolute_url())

@method_decorator(login_required, name='dispatch')
class AliasDelete(View):
    def get(self, request, *args, **kwargs):
        # get the alias based on the name in the url
        alias = get_object_or_404(Alias, name=kwargs['name'])

        # make sure the person viewing this page is the owner
        if alias.user == request.user:

            # go to the delete confirmation page
            return render(request, 'aliases/alias_delete.html', {
                'alias': alias,
            })

        # bad stuff happening here
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        # get the alias based on the name in the url
        alias = get_object_or_404(Alias, name=kwargs['name'])

        # make sure the person who submitted this is the owner
        if alias.user == request.user:

            # delete the alias
            alias.delete()

            # redirect to the dashboard
            return redirect('dashboard')

        # bad stuff happening here
        else:
            raise Http404
