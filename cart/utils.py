from decimal import Decimal

from django.apps import apps
from django.db.models import DecimalField, F, Prefetch, Q, Value
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import ExpressionWrapper, OuterRef, Subquery
from django.db.models.functions import Coalesce
from products.models import Product

from .models import Cart, ItemCart


class CartMixin:
    cart = None
    cart_info = None
    items = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            DocumentProductPrice = apps.get_model(
                'documents', 'DocumentProductPrice')
            self.cart = Cart.objects.filter(
                user=request.user, is_active=True).first()

            items = ItemCart.objects.get_items(self.cart)

            self.cart_info = items.aggregate(
                total_amount_discount=Coalesce(
                    Sum('total_price_discount', output_field = DecimalField()),
                    Value(0)
                ),
                total_amount_no_discount = Coalesce(
                    Sum('total_price_no_discount', output_field = DecimalField()),
                    Value(0)
                ),
                economy = Coalesce(
                    Sum('total_price_no_discount', output_field = DecimalField()) - Sum('total_price_discount', output_field = DecimalField()),
                    Value(0)
                ),
                total_quantity = Coalesce(
                    Sum('total_quantity_prod', output_field = DecimalField()),
                    Value(0)
                ),
                quantity = Count('id', filter=Q(cart=self.cart))
            )
        return super().dispatch(request, *args, **kwargs)
