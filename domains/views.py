from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from .models import Domain


class DomainListView(ListView):
    model = Domain

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domains'] = Domain.objects.filter(user=self.request.user)
        return context
