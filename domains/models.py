from django.contrib.auth.models import User
from django.db import models


class Domain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    is_blocked = models.BooleanField(default=False)
