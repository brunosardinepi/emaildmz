from django.contrib import admin

from .models import Filter


class FilterAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_blocked',)
    ordering = list_display

admin.site.register(Filter, FilterAdmin)
