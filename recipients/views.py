from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import RecipientForm
from .models import Recipient
from aliases.models import Alias
from emaildmz.utils import get_form_errors


@method_decorator(login_required, name='dispatch')
class RecipientCreate(View):
    def post(self, request, *args, **kwargs):
        # create the form with the POST data
        form = RecipientForm(request.POST)

        if form.is_valid():
            # assign the recipient to this user and alias, then save
            recipient = form.save(commit=False)
            recipient.user = self.request.user
            recipient.alias = get_object_or_404(Alias, name=kwargs['alias_name'])
            recipient.save()

        else:
            # process form errors
            get_form_errors(request, form)

        # whether it's a good form or not, take them to the dashboard
        return redirect(recipient.alias.get_absolute_url())

@method_decorator(login_required, name='dispatch')
class RecipientDelete(View):
    def get(self, request, *args, **kwargs):
        # get the recipient based on the pk in the url
        recipient = get_object_or_404(Recipient, pk=kwargs['pk'])

        # make sure the person viewing this page is the owner
        if recipient.user == request.user:

            # go to the delete confirmation page
            return render(request, 'recipients/recipient_delete.html', {
                'recipient': recipient,
            })

        # bad stuff happening here
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        # get the recipient based on the name in the url
        recipient = get_object_or_404(Recipient, pk=kwargs['pk'])

        # store the recipient's alias for the redirect later
        alias = recipient.alias

        # make sure the person who submitted this is the owner
        if recipient.user == request.user:

            # delete the recipient
            recipient.delete()

            # redirect to the dashboard
            return redirect(alias.get_absolute_url())

        # bad stuff happening here
        else:
            raise Http404
