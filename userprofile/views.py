from django.db.models import Q
from django.shortcuts import render
from django.db.models.expressions import F, OrderBy
from django.db.models.query import Prefetch
from django.http import request
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from order.models import Customer
from products.models import Product
from store.utils import BaseListView
from waitinglist.models import WaitingList
from order.models import Order
from .forms import UserCustomForm
from django.core.paginator import Paginator


class UserProfile(BaseListView, TemplateView):
    template_name = 'user.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            page_number = request.GET.get('page')
            customer = Customer.objects.filter(user=self.request.user).first()
            orders = Order.objects.filter(Q(customer=customer) & ~Q(status__in=[Order.STATUS_NEW_ORDER, Order.STATUS_CANCELED_ORDER])).select_related('cart').prefetch_related(
                'cart__items').prefetch_related('cart__items__product').prefetch_related('cart__items__product__brand').all().order_by('-date_of_reg')
            obj = Product.objects.get_products()
            favorite_products = obj.filter(
                Q(action__user=self.request.user), Q(action__favorite=True)).all()
            paginator = Paginator(orders, 5)
            page_obj = paginator.get_page(page_number)
            waiting_products = obj.filter(
                waiting__email=self.request.user.email).prefetch_related(
                Prefetch(
                    'waiting',
                    queryset=WaitingList.objects.all()
                )).annotate(
                    email=F('waiting__email')
            ).all()

            initial = {
                'username': self.request.user.username,
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
            }
            if customer:
                initial.update({
                    'address': customer.address,
                    'phone': customer.phone
                })
            counter_orders = Order.objects.filter(customer=customer).all()
            context = {
                'orders': orders,
                'waiting_list': waiting_products,
                'user_form': UserCustomForm(initial=initial),
                'favorite_products': favorite_products,
                'page_obj': page_obj,
                'cart_info': self.cart_info,
                'title': 'Профиль покупателя',
                'count_orders': len(counter_orders),
                'count_orders_fail': len(counter_orders.filter(status=Order.STATUS_CANCELED_ORDER)),
                'count_orders_wait': len(counter_orders.filter(status=Order.STATUS_WAIT_BUY_ORDER))
            }
            return render(request, self.template_name, context)
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        form = UserCustomForm(self.request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']
            customer = Customer.objects.get(user=self.request.user)
            customer.phone = phone
            customer.address = address
            customer.save()
            self.request.user.username = username
            self.request.user.email = email
            self.request.user.first_name = first_name
            self.request.user.last_name = last_name
            self.request.user.save()
        return HttpResponseRedirect(reverse_lazy('profile'))


#    def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#         customer = Customer.objects.filter(user=self.request.user).first()
#         orders = Order.objects.filter(Q(customer=customer) & ~Q(status__in=[Order.STATUS_NEW_ORDER, Order.STATUS_CANCELED_ORDER])).select_related('cart').prefetch_related(
#             'cart__items').prefetch_related('cart__items__product').prefetch_related('cart__items__product__brand').all().order_by('-date_of_reg')
#         obj = Product.objects.get_products()
#         favorite_products = obj.filter(Q(action__user=self.request.user), Q(action__favorite=True)).all()
#         waiting_products = obj.filter(
#             waiting__email=self.request.user.email).prefetch_related(
#             Prefetch(
#                 'waiting',
#                 queryset=WaitingList.objects.all()
#             )).annotate(
#                 email=F('waiting__email')
#             ).all()

#         initial = {
#             'username': self.request.user.username,
#             'first_name': self.request.user.first_name,
#             'last_name': self.request.user.last_name,
#             'email': self.request.user.email,
#         }
#         if customer:
#             initial.update({
#                 'address': customer.address,
#                 'phone': customer.phone
#             })
#         context['orders'] = orders
#         context['waiting_list'] = waiting_products
#         context['user_form'] = UserCustomForm(initial=initial)
#         context['favorite_products'] = favorite_products
#         return context
