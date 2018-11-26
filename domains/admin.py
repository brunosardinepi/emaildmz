from django.contrib import admin

from . import models


class DomainAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_blocked',)
    ordering = list_display

admin.site.register(models.Domain, DomainAdmin)
