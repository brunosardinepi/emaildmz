from .models import Alias, ForwardingEmail


def get_user_alias(user):
    # get the user's alias if one exists
    try:
        alias = Alias.objects.get(user=user)
    # otherwise, return None
    except Alias.DoesNotExist:
        alias = None

    return alias

def get_user_forwardingemails(user):
    # find the user's ForwardingEmails
    forwarding_emails = ForwardingEmail.objects.filter(user=user).values_list(flat=True)
    # add the user's login email
    forwarding_emails.append(user.email)

    return forwarding_emails
