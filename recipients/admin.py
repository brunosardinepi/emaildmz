from django.contrib import admin

from . import models


class RecipientAdmin(admin.ModelAdmin):
    list_display = ('user', 'email',)
    ordering = list_display

admin.site.register(models.Recipient, RecipientAdmin)
