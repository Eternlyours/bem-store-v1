from django.db import models
from documents.models import DocumentProductQuantity
from order.models import Order


class ProductsDashboard(DocumentProductQuantity):
    class Meta:
        proxy = True
        verbose_name = 'Отчёт по заказам и продуктам'
        verbose_name_plural = 'Отчёты по заказам и продуктам'

    