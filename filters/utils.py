from .models import Filter


def get_user_filters(user):
    # get the user's Filters
    return Filter.objects.filter(user=user)

def get_alias_filters(alias):
    # get the user's Aliases
    return Filter.objects.filter(alias=alias).order_by('name')
