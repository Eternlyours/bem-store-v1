from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models

from .forms import NewsOverrideAdminForm, ServiceOverrideAdminForm
from .models import News, Service


class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'active', 'body')
    list_display_links = ('id', 'title', 'body', 'active')
    search_fields = ('title', 'body', 'slug')
    readonly_fields = ('slug', 'date', 'get_views', )
    fields = ('slug', 'active', ('date', 'get_views'), 'title', 'body')

    form = NewsOverrideAdminForm


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'body')
    list_display_links = ('id', 'title', 'body')
    search_fields = ('title', 'body', 'slug')
    fields = ('slug', 'title', 'body')
    readonly_fields = ('slug',)

    form = ServiceOverrideAdminForm


admin.site.register(News, NewsAdmin)
admin.site.register(Service, ServiceAdmin)
