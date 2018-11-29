from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import AliasForm
from .models import Alias, ForwardingEmail
from .utils import get_user_aliases


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
            # put the errors into a dictionary to strip the html
            # this produces a key, value pair
            # where key is the field name and value is a list of errors
            for field, error_list in form.errors.get_json_data().items():
                for error in error_list:
                    # get the message from the list element
                    # and add it to the site messages as an error
                    messages.add_message(request, messages.ERROR, error['message'])

        # whether it's a good form or not, take them to the dashboard
        return redirect('dashboard')
