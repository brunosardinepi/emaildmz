from django.forms import ModelForm

from .models import Filter


class FilterForm(ModelForm):
    class Meta:
        model = Filter
        fields = ['name']
