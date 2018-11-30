from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Alias(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        verbose_name_plural = 'Aliases'

    def __str__(self):
        return "{}@emaildmz.com".format(self.name)

    def get_absolute_url(self):
        return reverse('dashboard', kwargs={'alias_name': self.name})

class ForwardingEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email
