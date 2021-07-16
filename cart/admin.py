from django.contrib import admin
from .models import Cart, ItemCart


class CartProductsAdmin(admin.TabularInline):
    model = ItemCart


class CartAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    inlines = (CartProductsAdmin, )
    readonly_fields = ('date', 'total_amount', 'total_quantity')
    list_display = ('user', 'date', 'is_active')
    list_display_links = ('user',)
    fields = ('user', 'date', 'is_active', 'updated_at', 'total_amount', 'total_quantity')
    list_filter = ['is_active',]

admin.site.register(Cart, CartAdmin)
