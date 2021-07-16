import datetime

import stripe
from application import settings
from cart.models import Cart
from cart.utils import CartMixin
from django.contrib import messages
from django.http import JsonResponse
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from order.models import Order

stripe.api_key = 'sk_test_51IjqzNETVNd9iyiLQLa4mfF1qhADNtQVTWWICjbHCtKKqxa9P9cqsgsiFsU4tuyJmqvUc7n9Cz2Emp7ppUQtniwr00aLFE18pd'


class PaymentView(CartMixin, View):
    template_name = 'payment.html'
    order = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                self.order = Order.objects.get(
                    id=kwargs['id'], status=Order.STATUS_WAIT_BUY_ORDER, customer__user=request.user)
            except:
                return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      {
                          'cart_info': self.cart_info,
                          'order': self.order,
                          'key': settings.STRIPE_PUB_KEY,
                          'title': 'Оплата'
                      }
                      )

    def post(self, request, *args, **kwargs):
        order = self.order
        cart = self.cart_info

        customer = stripe.Customer.create(
            email=request.user.email,
            name='{0} {1}'.format(request.user.first_name,
                                  request.user.last_name),
            phone=order.customer.phone,
            source=request.POST['stripeToken']
        )
        stripe.Charge.create(
            customer=customer,
            amount=int(cart['total_amount_discount']),
            currency='rub',
        )
        self.order.amount = cart['total_amount_discount']
        self.order.date_of_reg = datetime.datetime.now()
        self.order.status = Order.STATUS_PROGRESS_ORDER
        self.order.save()
        cart_obj = Cart.objects.get(order__id=order.id)
        cart_obj.is_active = False
        cart_obj.save()
        messages.add_message(
            request, messages.INFO, 'Мы приняли ваш заказ! В течении часа наши менеджеры свяжутся с вами. Перейдите в профиль для слежения за заказом'
        )
        return HttpResponseRedirect(reverse('home'))
