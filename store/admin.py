from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (Brand, Category, Customer)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')


class CategoryAdmin(MPTTModelAdmin):
    fields = ('slug', 'name', 'parent', 'icon')
    list_display = ('id', 'name', 'slug', 'parent', 'icon')
    list_display_links = ('name', 'slug', 'parent')
    readonly_fields = ('slug', )
    search_fields = ('id', 'name', 'slug')


admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Customer)

