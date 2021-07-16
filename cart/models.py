import uuid
from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models.expressions import ExpressionWrapper, F, Q, Subquery, OuterRef
from django.db.models import DecimalField
from django.db.models.aggregates import Sum, Count, IntegerField
from django.db.models.query import Prefetch, Value
from django.db.models.functions import Coalesce
from django.db.utils import cached_property
from decimal import Decimal
from products.models import Product, Discount
from django.apps import apps
from .managers import CartItemManager


class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name=u'cart', verbose_name=u'Покупатель', on_delete=models.CASCADE)
    date = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Дата создания')
    is_active = models.BooleanField(
        verbose_name=u'Активность корзины', default=True)
    updated_at = models.DateTimeField(
        verbose_name=u'Редактировано', null=True, blank=True)

    @cached_property
    def total_amount(self):       
        DocumentProductPrice = apps.get_model('documents', 'DocumentProductPrice')
        DocumentProductQuantity = apps.get_model('documents', 'DocumentProductQuantity')
        minus = Coalesce(
            Sum('quantity', filter = Q(type = DocumentProductQuantity.SPENDING_CHOICES)),
            Value(0)
        )
        plus = Coalesce(
            Sum('quantity', filter = Q(type = DocumentProductQuantity.COMING_CHOICES)),
            Value(0)
        )

        prices = DocumentProductPrice.objects.all().filter(
            product = OuterRef('product__id')).order_by(
            '-actual_date')
        quantities = DocumentProductQuantity.objects.all().filter(
            product = OuterRef('product__id')
        ).values('product').annotate(
            plus = plus,
            minus = minus,
            total_quantity = ExpressionWrapper(
                F('plus') - F('minus'),
                output_field = IntegerField()
            )
        )

        items = ItemCart.objects.filter(cart = self).select_related(
            'product'
        ).prefetch_related(
            Prefetch(
            'product__discount',
            queryset = Discount.objects.all()
        )).annotate(
            discount = Coalesce(
                Sum('product__discount__amount_discount', filter = Q(product__discount__amount_discount__gt = 0, product__discount__is_active=True)),
                Value(0)
            ),
            price=prices.values('price')[:1],
            price_discount=ExpressionWrapper(
                F('price') - (F('price') * F('discount') / Decimal(100)),
                output_field = DecimalField()
            )
        ).all()
        amount = 0
        for item in items:
            amount += item.price_discount * item.quantity
        return amount
    total_amount.short_description = 'Итоговая цена'

    @cached_property
    def total_quantity(self):
        return self.__class__.objects.filter(id=self.id).prefetch_related(
            Prefetch(
                'items',
                queryset=ItemCart.objects.select_related('cart').all()
            )
        ).aggregate(count=Count('items'))['count']
    total_quantity.short_description = 'Количество товаров'

    class Meta:
        verbose_name = 'Корзину покупателя'
        verbose_name_plural = 'Корзины покупателей'

    def __str__(self):
        return '{0} - {1}'.format(self.id, self.user.username)


class ItemCart(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, verbose_name=u'Продукт', on_delete=models.CASCADE, related_name='item')
    quantity = models.PositiveIntegerField(
        default=1, verbose_name=u'Количество')
    cart = models.ForeignKey(
        Cart, verbose_name=u'Корзина', on_delete=models.CASCADE, related_name='items')

    objects = CartItemManager()

    def __str__(self):
        return '{0} - {1}'.format(self.product.slug, self.quantity)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        update_cart(self)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'


def update_cart(product):
    cart = Cart.objects.get(items=product)
    cart.updated_at = datetime.now()
    cart.save()
