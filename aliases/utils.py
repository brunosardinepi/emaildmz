from .models import ForwardingEmail

def get_user_forwardingemails(user):
    # find the user's ForwardingEmails
    forwarding_emails = ForwardingEmail.objects.filter(user=user).values_list(flat=True)
    # add the user's login email
    forwarding_emails.append(user.email)

    return forwarding_emails
