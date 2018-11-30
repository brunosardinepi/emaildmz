from .models import Alias, ForwardingEmail


def get_user_aliases(user):
    # get the user's Aliases
    return Alias.objects.filter(user=user).order_by('name')

def get_user_forwardingemails(user):
    # get the user's ForwardingEmails
    return ForwardingEmail.objects.filter(user=user).order_by('email')

def get_alias_forwardingemails(alias):
    # get the alias's ForwardingEmails
    return ForwardingEmail.objects.filter(alias=alias).order_by('email')
