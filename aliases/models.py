from django.contrib.auth.models import User
from django.db import models


class Alias(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)

    class Meta:
        verbose_name_plural = 'Aliases'

    def __str__(self):
        return "{}@emaildmz.com".format(self.name)

class ForwardingEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email
