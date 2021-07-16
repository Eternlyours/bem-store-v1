import random
from datetime import datetime

from cart.models import Cart, ItemCart
from cart.utils import CartMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, F, Q
from django.http.response import HttpResponseRedirect
from application import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic.base import TemplateView, View
from django.core.mail import get_connection, send_mail
from products.models import Product
from store.models import Customer
from store.utils import BaseListView

from order.forms import CustomOrderForm
from order.models import Order


class OrderView(CartMixin, View):
    template_name = 'order.html'
    cart = None
    order = None
    customer = None
    items = None
    conditions = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.cart = Cart.objects.filter(
                user=request.user, is_active=True, items__isnull=False).first()
            self.conditions = ItemCart.objects.filter(cart=self.cart).select_related(
                'product').all().aggregate(
                delivery=Count('product__delivery',
                               filter=Q(product__delivery=False)),
                type_buy=Count('product__type_buy', filter=Q(
                    product__type_buy=Product.UNDER_THE_ORDER))
            )
            self.items = ItemCart.objects.get_items(cart=self.cart)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if self.cart is None:
                return HttpResponseRedirect(reverse('home'))
            initial = {}
            initial = {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email
            }
            customer = Customer.objects.filter(user=request.user).first()
            order = Order.objects.filter(
                cart=self.cart, customer=customer
            ).first()
            if customer:
                initial.update({
                    'address': customer.address,
                    'phone': customer.phone,
                })
            if self.conditions:
                initial.update({
                    'type_buy_hidden': self.conditions['type_buy'],
                    'type_delivery_hidden': self.conditions['delivery']
                })
            if order:
                initial.update({
                    'comment': order.comment,
                    'type_delivery': order.type_delivery,
                    'type_buy': order.buy,
                })
            form = CustomOrderForm(initial=initial)
        else:
            return HttpResponseRedirect('/')
        return render(request, self.template_name, {'cart': self.cart, 'items': self.items, 'form': form, 'conditions': self.conditions, 'cart_info': self.cart_info, 'title': 'Оформление заказа'})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, order_created = Order.objects.get_or_create(
            cart=Cart.objects.filter(user=request.user,
                                     is_active=True, items__isnull=False).first(), customer=customer
        )

        order_form = CustomOrderForm(request.POST)
        if order_form.is_valid() and request.recaptcha_is_valid:        
            cart = Cart.objects.get(user=request.user, is_active=True)
            items = ItemCart.objects.filter(cart=cart).select_related(
                'product').all().aggregate(
                delivery=Count('product__delivery',
                               filter=Q(product__delivery=False)),
                type_buy=Count('product__type_buy', filter=Q(
                    product__type_buy=Product.UNDER_THE_ORDER))
            )
            goods = ItemCart.objects.get_items(cart=cart)

            errors = False

            if goods:
                goods_message = ''
                counter_product_message = ''
                for good in goods:
                    if good.product.get_actual_quantity['total_quantity'] <= 0:
                        goods_message += format_html('{}, ',
                                                     good.product.model)
                    if good.product.get_actual_quantity['total_quantity'] < good.quantity and good.product.get_actual_quantity['total_quantity'] > 0:
                        counter_product_message += format_html('{0} количество: {1}, в наличии только - {2}, ',
                                                               good.product.model, good.quantity, good.product.get_actual_quantity['total_quantity'])

                if goods_message:
                    messages.add_message(
                        request, messages.INFO, 'К сожалению данные товары - {} закончились на складе. Вы можете подписаться на эти товары или удалить их.'.format(
                            goods_message)
                    )
                    errors = True
                if counter_product_message:
                    messages.add_message(
                        request, messages.INFO, 'Недостаточно товаров на складе - {}'.format(
                            counter_product_message)
                    )
                    errors = True

            if items['type_buy'] > 0 and order_form.cleaned_data['type_buy'] == Order.TYPE_CASH_PAYMENT:
                messages.add_message(
                    request, messages.INFO, 'Покупка под заказ осуществляется после полной предоплаты!'
                )
                errors = True
            if items['delivery'] > 0 and order_form.cleaned_data['type_delivery'] == Order.TYPE_DELIVERY_DELIVERY:
                messages.add_message(
                    request, messages.INFO, 'Пожалуйста, выберите вариант доставки соответствующий с условиями заказа'
                )
                errors = True

            if errors:
                order.delete()
                return HttpResponseRedirect('/checkout')
            customer.address = order_form.cleaned_data['address']
            customer.phone = order_form.cleaned_data['phone']
            order.comment = order_form.cleaned_data['comment']
            order.type_delivery = order_form.cleaned_data['type_delivery']
            order.buy = order_form.cleaned_data['type_buy']
            self.request.user.email = order_form.cleaned_data['email']
            self.request.user.first_name = order_form.cleaned_data['first_name']
            self.request.user.last_name = order_form.cleaned_data['last_name']
            if order_form.cleaned_data['type_buy'] == Order.TYPE_CARD_PAYMENT:
                order.status = Order.STATUS_WAIT_BUY_ORDER
                order.date_of_reg = datetime.now()
                customer.save()
                order.save()
                request.user.save()
                return HttpResponseRedirect(reverse('payment', kwargs={'id': order.id}))
            if order_form.cleaned_data['type_buy'] == Order.TYPE_CASH_PAYMENT:
                order.status = Order.STATUS_PROGRESS_ORDER
                order.amount = cart.total_amount
                order.date_of_reg = datetime.now()
                cart.is_active = False
                cart.save()
                customer.save()
                order.save()
                request.user.save()
                messages.success(
                    request, 'Мы приняли ваш заказ! В течении часа наши менеджеры свяжутся с вами. Перейдите в профиль для слежения за заказом')
                return HttpResponseRedirect(reverse('home'))            
                
        else:
            return render(request, self.template_name, {'cart': self.cart, 'items': self.items, 'form': order_form, 'conditions': self.conditions, 'title': 'Оформление заказа'})
        return HttpResponseRedirect(reverse('checkout'))


class SuccessOrderView(BaseListView, TemplateView):
    template_name = 'current-order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Order.objects.filter(~Q(status=Order.STATUS_ISSUED_ORDER) |
                                        ~Q(status=Order.STATUS_NEW_ORDER))
        obj = get_object_or_404(
            queryset, customer__user=self.request.user)
        context['order'] = obj
        return context


def removeOrder(request, id):
    if request.user.is_authenticated:
        queryset = Order.objects.filter(status__in=[
                                        Order.STATUS_WAIT_BUY_ORDER, Order.STATUS_NEW_ORDER], customer__user=request.user).all()
        order = get_object_or_404(queryset, id=id)
        order.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
