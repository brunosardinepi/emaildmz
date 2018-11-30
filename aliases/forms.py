from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Alias


class AliasForm(ModelForm):
    class Meta:
        model = Alias
        fields = ['name']
        error_messages = {
            'name': {
                'unique': _("Someone is already using this alias. Try a different one."),
            },
        }
