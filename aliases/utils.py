from .models import Alias, ForwardingEmail


def get_user_aliases(user):
    # get the user's Aliases
    return Alias.objects.filter(user=user)

def get_user_forwardingemails(user):
    # get the user's ForwardingEmails
    return ForwardingEmail.objects.filter(user=user)
