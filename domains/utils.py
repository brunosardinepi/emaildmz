from .models import Domain


def get_user_domains(user):
    # get the user's Domains
    return Domain.objects.filter(user=user)

def get_alias_domains(alias):
    # get the user's Aliases
    return Domain.objects.filter(alias=alias).order_by('name')
