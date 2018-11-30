from django.forms import ModelForm

from .models import Recipient


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = ['email']
