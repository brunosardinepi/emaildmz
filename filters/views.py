from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import FilterForm
from .models import Filter
from aliases.models import Alias
from emaildmz.utils import get_form_errors


@method_decorator(login_required, name='dispatch')
class FilterCreate(View):
    def post(self, request, *args, **kwargs):
        # create the form with the POST data
        form = FilterForm(request.POST)

        if form.is_valid():
            # assign the filter to this user and alias, then save
            filter = form.save(commit=False)
            filter.user = self.request.user
            filter.alias = get_object_or_404(Alias, name=kwargs['alias_name'])
            filter.save()

        else:
            # process form errors
            get_form_errors(request, form)

        # whether it's a good form or not, take them to the dashboard
        return redirect(filter.alias.get_absolute_url())

@method_decorator(login_required, name='dispatch')
class FilterDelete(View):
    def get(self, request, *args, **kwargs):
        # get the filter based on the pk in the url
        filter = get_object_or_404(Filter, pk=kwargs['pk'])

        # make sure the person viewing this page is the owner
        if filter.user == request.user:

            # go to the delete confirmation page
            return render(request, 'filters/filter_delete.html', {
                'filter': filter,
            })

        # bad stuff happening here
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        # get the filter based on the pk in the url
        filter = get_object_or_404(Filter, pk=kwargs['pk'])

        # store the filter's alias for the redirect later
        alias = filter.alias

        # make sure the person who submitted this is the owner
        if filter.user == request.user:

            # delete the filter
            filter.delete()

            # redirect to the dashboard
            return redirect(alias.get_absolute_url())

        # bad stuff happening here
        else:
            raise Http404

@method_decorator(login_required, name='dispatch')
class FilterFilter(View):
    def get(self, request, *args, **kwargs):
        # get the filter based on the pk in the url
        filter = get_object_or_404(Filter, pk=kwargs['pk'])

        # make sure the person who submitted this is the owner
        if filter.user == request.user:

            # determine the action
            if kwargs['action'] == "allow":
                # set the filter to "allowed"
                filter.is_blocked = False

            elif kwargs['action'] == "block":
                # set the filter to "blocked"
                filter.is_blocked = True

            else:
                # this isn't an option
                raise Http404

            # save the changes
            filter.save()

            # redirect to the dashboard
            return redirect(filter.alias.get_absolute_url())

        # bad stuff happening here
        else:
            raise Http404
