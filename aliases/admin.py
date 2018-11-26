from django.contrib import admin

from . import models


class AliasAdmin(admin.ModelAdmin):
    list_display = ('user', 'name',)
    ordering = list_display

class ForwardingEmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'email',)
    ordering = list_display

admin.site.register(models.Alias, AliasAdmin)
admin.site.register(models.ForwardingEmail, ForwardingEmailAdmin)
