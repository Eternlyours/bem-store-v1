from django.db import models
from django.db.models import FloatField, IntegerField, DecimalField, OuterRef, Subquery
from django.db.models.expressions import ExpressionWrapper, F, Q
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.db.models.query import Value
from django.apps import apps
from decimal import Decimal


class CartItemManager(models.Manager):

    def get_items(self, cart):
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
                            product=OuterRef('product__id')).order_by(
                            '-actual_date')
        quantities = DocumentProductQuantity.objects.all().filter(
            product=OuterRef('product__id')
        ).values('product').annotate(
            plus=plus,
            minus=minus,
            total_quantity=ExpressionWrapper(
                F('plus')-F('minus'),
                output_field = IntegerField()
            )
        )
        # .prefetch_related(
        #     'product__info'
        # )
        return self.filter(cart=cart).select_related(
            'product'
        ).prefetch_related(
            'product__discount'
        ).prefetch_related(
            'product__brand'
        ).prefetch_related(
            'product__category'
        ).prefetch_related(
            'product__images'
        ).annotate(
                price=prices.values('price')[:1],
                discount=Coalesce(
                    Sum('product__discount__amount_discount', filter=Q(
                        product__discount__amount_discount__gt=0, product__discount__is_active=True)),
                    Value(0)
                ),
                price_discount=ExpressionWrapper(
                    F('price') - (F('price') * F('discount') / Decimal(100)),
                    output_field=DecimalField()
                ),
                total_price_discount=ExpressionWrapper(
                    F('quantity') * F('price_discount'),
                    output_field=DecimalField()
                ),
                total_quantity_prod=F('quantity'),
                total_price_no_discount=ExpressionWrapper(
                    F('quantity') * F('price'),
                    output_field=DecimalField()
                ),
                total_quantity=quantities.values('total_quantity')
        ).all()

    def add(self, product, cart, quantity):
        item, created = self.get_or_create(product=product, cart=cart)
        if not created:
            item.quantity = F('quantity') + quantity
        else:
            item.quantity = quantity
        item.save()
        return created

    # def delete(self, product, cart):
    #     cart = Cart.objects.get(items=product)
    #     cart.updated_at = datetime.now()
    #     cart.save()
    #     return self.filter(product=product, cart=cart).delete()
