from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Recipient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.ForeignKey('aliases.Alias', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email


