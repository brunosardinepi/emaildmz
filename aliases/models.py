from django.contrib.auth.models import User
from django.db import models


class Alias(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)

    class Meta:
        verbose_name_plural = 'Aliases'

class ForwardingEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
