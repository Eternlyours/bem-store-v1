from django.db import models
from order.models import Order
from cart.models import Cart, ItemCart
from store.models import Customer


class OrderBoard(Order):
    class Meta:
        proxy = True
        verbose_name = 'Доска заказов'
        verbose_name_plural = 'Доска заказов'