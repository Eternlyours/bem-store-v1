from cart.models import Cart, ItemCart
from django.contrib import admin

from django.utils.html import format_html

from .models import Customer, Order

class OrderAdmin(admin.ModelAdmin):

    date_hierarchy = 'date'
    list_filter = ('status', 'buy', 'type_delivery')
    list_display = ('customer', 'status', 'date', 'amount')
    list_display_links = ('customer', 'status')
    readonly_fields = ('id','key', 'is_confirm', 'cart', 'customer', 'amount', 'comment_safe',
                       'date', 'type_delivery', 'buy', 'get_customer', 'get_cart', 'date_of_reg')
    sortable_by = ('date', 'amount')
    fields = ('id', 'key', 'date_of_reg' , 'is_confirm', 'get_customer', 'get_cart', 'date', 'amount',
              'status', 'buy', 'type_delivery', 'comment_safe')

    def get_customer(self, obj):
        customer = Customer.objects.filter(order=obj).first()
        user = customer.user
        html = '''
            <p>Покупатель: {0} {1}</p>
            <p>Электронная почта: {2}</p>
            <p>Телефон: {3}</p>
            <p>Адрес: {4}</p>
        '''
        return format_html(html, user.first_name, user.last_name, user.email, customer.phone, customer.address)
    get_customer.short_description = 'Данные о покупателе'
    get_customer.allow_tags = True

    def get_cart(self, obj):
        cart = Cart.objects.filter(order=obj).first()
        items = ItemCart.objects.get_items(cart)
        table = '''
        <table> 
            <thead> 
                <tr> <td>Артикул</td><td>Наименование</td><td>Цена</td><td>Количество</td> </tr> 
            </thead> 
            <tbody>
        '''
        for i in items:
            table += format_html('<tr> <td>{}</td><td>{}</td><td>{}</td><td>{}</td> </tr>',
                                 i.product.article, i.product.brand.name + ' ' + i.product.model, i.total_price_discount, i.quantity)
        table += '</tbody></table>'
        return format_html(table)
    get_cart.short_description = 'Товары'
    get_cart.allow_tags = True


admin.site.register(Order, OrderAdmin)