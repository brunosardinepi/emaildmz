from django.contrib.auth.models import User
from django.db import models


class Filter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.ForeignKey('aliases.Alias', on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

