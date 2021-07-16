from django.db import models
from django.apps import apps
from django.db.models.functions import Coalesce
from django.db.models.aggregates import Sum, Avg, IntegerField
from django.db.models.expressions import ExpressionWrapper
from django.db.models import Value, FloatField, F, Q, DecimalField, Subquery, OuterRef
from django.db.models.query import Prefetch
from decimal import Decimal


class ProductManager(models.Manager):

    def get_products(self):
        Discount = apps.get_model('products', 'Discount')
        ProductCharacteristic = apps.get_model(
            'products', 'ProductCharacteristic')
        Photo = apps.get_model('products', 'Photo')
        DocumentProductPrice = apps.get_model('documents', 'DocumentProductPrice')
        DocumentProductQuantity = apps.get_model('documents', 'DocumentProductQuantity')
        ProductUserAction = apps.get_model('products', 'ProductUserAction')

        minus = Coalesce(
            Sum('quantity', filter = Q(type = DocumentProductQuantity.SPENDING_CHOICES)),
            Value(0)
        )
        plus = Coalesce(
            Sum('quantity', filter = Q(type = DocumentProductQuantity.COMING_CHOICES)),
            Value(0)
        )

        prices = DocumentProductPrice.objects.all().filter(
                            product=OuterRef('pk')).order_by(
                            '-actual_date')
        quantities = DocumentProductQuantity.objects.all().filter(
            product=OuterRef('pk')
        ).values('product').annotate(
            plus=plus,
            minus=minus,
            total_quantity=ExpressionWrapper(
                F('plus')-F('minus'),
                output_field = IntegerField()
            )
        )
        rating = ProductUserAction.objects.all().filter(
            product=OuterRef('pk')
        ).values('product').annotate(
            rating = Avg('rate')
        )
     
        queryset = self.all().filter(active=True).select_related(
            'brand').select_related(
            'category').prefetch_related(
            Prefetch(
                'images',
                queryset=Photo.objects.all()
            )).prefetch_related(
            Prefetch(
                'characteristic',
                queryset=ProductCharacteristic.objects.all()
            )).prefetch_related(
            Prefetch(
                'discount',
                queryset=Discount.objects.all()
            )).annotate(
            price_doc=prices.values('price')[:1],
            quantity=quantities.values('total_quantity'),
            popular=quantities.values('minus'),
            buy=F('type_buy'),
            avg = rating.values('rating'),
            discount_sum=Coalesce(
                Sum('discount__amount_discount', filter=Q(
                    discount__amount_discount__gt=0, discount__is_active=True)),
                Value(0)
            )
            ,
            price_discount=ExpressionWrapper(
                F('price_doc') - (F('price_doc') * F('discount_sum') / Decimal(100)),
                output_field = DecimalField()
            ),
            price_filter = ExpressionWrapper(
                F('price_discount'),
                output_field=FloatField()
            )
        ).order_by('-id')

        return queryset

    def get_products_by_category(self, param):
        return self.filter(Q(
            category__parent__slug=param.split('/')[-1])
            | Q(category__slug=param.split('/')[-1]))

    def sort(self, attr):
        return self.get_products().order_by('-price')
