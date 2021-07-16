from django.db.models.expressions import ExpressionWrapper, F, Value
from django.db.models.fields import DecimalField, IntegerField
from django.db.models.functions.math import Exp
from dashboard.models import ProductsDashboard
from django.db.models import DateTimeField
from django.contrib import admin
from django.db.models.aggregates import Count, Sum, Min, Max
from django.db.models.query import Q
from django.db.models.functions import Coalesce, Trunc
from django.apps import apps


@admin.register(ProductsDashboard)
class ProductDashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard-list.html'
    date_hierarchy = 'actual_date_doc'
    list_filter = ('product__category__name',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        DocumentProductQuantity = apps.get_model(
            'documents', 'DocumentProductQuantity')
        DocumentProductPrice = apps.get_model(
            'documents', 'DocumentProductPrice')

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('product'),
            'total_quantity': Sum('quantity', filter=Q(type=DocumentProductQuantity.SPENDING_CHOICES)),
            'total_amount': Sum('price', filter=Q(type=DocumentProductQuantity.SPENDING_CHOICES))
        }

        response.context_data['summary'] = list(
            qs
            .values('product__category__name')
            .annotate(**metrics)
            .order_by('-total_amount')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period


        summary_over_time = qs.annotate(
            period=Trunc('actual_date_doc', period, output_field=DateTimeField()),
        ).values('period').annotate(total=Sum('price')).order_by('period')
        
        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        
        high = summary_range.setdefault('high', 0) or 0
        low = summary_range.setdefault('low', 0) or 0 
        
        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'pct': \
               ((x['total'] or 0) - low) / (high - low) * 100
               if high > low else 0,
        } for x in summary_over_time]

        metrics_balance = {
            'total_quantity': Coalesce(
                Sum('quantity', filter=Q(type=DocumentProductQuantity.COMING_CHOICES)),
                Value(0)
            ),
            'quantity': Coalesce(
                Sum('quantity', filter=Q(type=DocumentProductQuantity.SPENDING_CHOICES)),
                Value(0)
            ),
            'balance': ExpressionWrapper(
                F('total_quantity') - F('quantity'),
                output_field=IntegerField()
            )
        }

        response.context_data['products_balance'] = list(
            qs
            .values('product__category__name')
            .annotate(**metrics_balance)
            .order_by('-balance')
        )

        return response


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'
    if date_hierarchy + '__month' in request.GET:
        return 'day'
    if date_hierarchy + '__year' in request.GET:
        return 'week'
    return 'month'