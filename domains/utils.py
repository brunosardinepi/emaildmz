from .models import Domain


def get_user_domains(user):
    # get the user's Domains
    return Domain.objects.filter(user=user)
