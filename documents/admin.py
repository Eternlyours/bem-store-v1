from django.contrib import admin
from .models import DocumentProductPrice, DocumentProductQuantity

class DocumentProductQuantityAdmin(admin.ModelAdmin):
    fields = ('product', 'actual_date_doc', 'actual_date', 'quantity', 'type')
    readonly_fields = ('actual_date_doc', )
    list_filter = ('type', 'product__category__name')
    list_display = ('product', 'quantity', 'type', )
    list_display_links = ('product', )


class DocumentProductPriceAdmin(admin.ModelAdmin):
    fields = ('product', 'actual_date', 'price')
    list_display = ('product', 'actual_date', 'price', )
    list_display_links = ('product', )
    date_hierarchy = 'actual_date'


admin.site.register(DocumentProductPrice, DocumentProductPriceAdmin)
admin.site.register(DocumentProductQuantity, DocumentProductQuantityAdmin)
