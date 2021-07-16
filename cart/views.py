from decimal import Decimal

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, FloatField
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import (ExpressionWrapper, F, OuterRef, Q,
                                          Subquery)
from django.db.models.functions import Coalesce
from django.db.models.query import Prefetch, Value
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views.generic.base import TemplateView, View
from products.models import Product

from .models import Cart, ItemCart, update_cart
from .utils import CartMixin
from django.apps import apps


@login_required(login_url='login')
def add_to_cart(request, slug):
    cart, created = Cart.objects.get_or_create(
        user=request.user, is_active=True
    )
    quantity = request.POST.get('quantity', 1)
    product = get_object_or_404(Product, slug=slug)
    Order = apps.get_model('order', 'Order')
    order_check = Order.objects.filter(customer__user=request.user, status=Order.STATUS_WAIT_BUY_ORDER).exists()
    if order_check:
        messages.add_message(request, messages.INFO, 'Пожалуйста, оплатите или отмените прошлые заказы.')                
        return HttpResponseRedirect(reverse('detail-product', kwargs={'slug': slug}))
    balance_product = Product.objects.filter(
        id=product.pk).first()
    if balance_product.get_actual_quantity['total_quantity'] <= 0:
        messages.add_message(request, messages.INFO,
                             'Товар отсутствует на складе')
        return HttpResponseRedirect(reverse('detail-product', kwargs={'slug': balance_product.slug}))
    if balance_product.get_actual_quantity['total_quantity'] < int(quantity):
        messages.add_message(request, messages.INFO,
                             'Недостаточно товара на складе')
        return HttpResponseRedirect(reverse('detail-product', kwargs={'slug': balance_product.slug}))
    if int(quantity) <= 0:
        messages.add_message(request, messages.INFO,
                             'Введите корректное количество')
        return HttpResponseRedirect(reverse('detail-product', kwargs={'slug': balance_product.slug}))
    ItemCart.objects.add(product, cart, quantity)
    messages.success(request, 'Товар успешно добавлен в корзину')
    return HttpResponseRedirect(reverse('cart'))


@login_required(login_url='login')
def delete_cart(request, slug):
    item = ItemCart.objects.filter(
        product__slug=slug, cart__user=request.user, cart__is_active=True)
    cart = Cart.objects.filter(user=request.user, is_active=True).annotate(
        count=Count('items')).first()
    if item:
        update_cart(item.first())
        item.delete()
        if cart.count == 1:
            cart.delete()
        messages.success(request, 'Товар успешно удалён из корзины')
    else:
        messages.success(request, 'Товар не был найден в корзине!')
    return HttpResponseRedirect(reverse('cart'))


class CartView(CartMixin, TemplateView):
    template_name = 'cart.html'
    items = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            self.items = ItemCart.objects.get_items(self.cart)
            conditions = ItemCart.objects.filter(cart=self.cart).select_related(
                'product').all().aggregate(
                delivery=Count('product__delivery',
                               filter=Q(product__delivery=False)),
                type_buy=Count('product__type_buy', filter=Q(
                    product__type_buy=Product.UNDER_THE_ORDER))
            )
            context['cart_info'] = self.cart_info
            context['cart'] = self.cart
            context['title'] = 'Корзина'
            context['items'] = self.items
            context['conditions']  = conditions
        context['choice_list'] = ['товар', 'товара', 'товаров']
        return context

    def post(self, request):
        product = request.POST.get('product')
        quantity = request.POST.get('quantity')
        item = ItemCart.objects.get(
            product__slug=product, cart__user=request.user, cart__is_active=True)
        item.quantity = quantity
        item.save()
        return HttpResponseRedirect(self.request.path_info)
