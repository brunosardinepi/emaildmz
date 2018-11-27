from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from .models import Alias, ForwardingEmail
from .utils import get_user_alias


class ForwardingEmailListView(ListView):
    model = ForwardingEmail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alias'] = get_user_alias(self.request.user)
        return context
