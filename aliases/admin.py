from django.contrib import admin

from . import models


class AliasAdmin(admin.ModelAdmin):
    list_display = ('user', 'name',)
    ordering = list_display

admin.site.register(models.Alias, AliasAdmin)
