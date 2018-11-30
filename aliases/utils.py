from .models import Alias
from recipients.models import Recipient


def get_alias_recipients(alias):
    # get the alias's Recipients
    return Recipient.objects.filter(alias=alias).order_by('email')

def get_user_aliases(user):
    # get the user's Aliases
    return Alias.objects.filter(user=user).order_by('name')
