from decimal import Decimal

from blog.models import News
from cart.models import Cart
from cart.utils import CartMixin
from consultation.forms import DiagnosticForm
from django.db.models import Prefetch, Q
from django.template.defaultfilters import slugify
from products.forms import FilterForm, SortForm
from products.models import ProductCharacteristic
from unidecode import unidecode

from store.forms import SearchForm

from .models import Category, Customer


def filtering(form, queryset):
    category = form.cleaned_data['category']
    brand = form.cleaned_data['brand']
    max_p = form.cleaned_data['max_price']
    min_p = form.cleaned_data['min_price']
    quantity = form.cleaned_data['quantity']

    if category:
        queryset = queryset.filter(
            Q(category__slug__in=category) | Q(
                category__parent__slug__in=category))
    if brand:
        queryset = queryset.filter(brand__name=brand)
    if quantity == 'in-stock':
        queryset = queryset.filter(
            quantity__gt=0
        )
    if quantity == 'out-of-stock':
        queryset = queryset.filter(
            quantity=0
        )
    if max_p:
        queryset = queryset.filter(
            price_filter__lte=max_p
            )
    if min_p:
        queryset = queryset.filter(
            price_filter__gte=min_p
            )
    params = ProductCharacteristic.objects.values(
        'name', 'unit').distinct().all()

    for param in params:
        name = slugify(unidecode(param['name']))
        _max_name = 'max_{0}'.format(name)
        _min_name = 'min_{0}'.format(name)
        if name in form.cleaned_data:
            def_param = form.cleaned_data[name]
            if def_param:
                queryset = queryset.filter(
                    Q(characteristic__name=param['name']),
                    Q(characteristic__text_value__in=def_param))
        if _max_name in form.cleaned_data:
            max_param = form.cleaned_data[_max_name]
            if max_param:
                queryset = queryset.filter(
                    Q(characteristic__name=param['name']),
                    Q(characteristic__decimal_value__lte=max_param)
                )
        if _min_name in form.cleaned_data:
            min_param = form.cleaned_data[_min_name]
            if min_param:
                queryset = queryset.filter(
                    Q(characteristic__name=param['name']),
                    Q(characteristic__decimal_value__gte=min_param)
                )
    return queryset


def sorting(form, queryset):
    price = form.cleaned_data['sort_price']
    rate = form.cleaned_data['sort_rate']
    if price:
        queryset = queryset.order_by(price)
    if rate:
        queryset = queryset.order_by(rate)
    return queryset


class BaseFormView:
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}
        for item in dict(self.request.GET):
            if len(dict(self.request.GET)[item]) == 1:
                initial.update({item: self.request.GET[item]})
            else:
                initial.update({item: dict(self.request.GET)[item]})
        context['filter_form'] = FilterForm(initial=initial)
        return context


class BaseListView(CartMixin):
    template_name = None
    queryset = None
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        form = FilterForm(self.request.GET)
        sort_form = SortForm(self.request.GET)
        if form.is_valid():
            self.queryset = filtering(form, self.queryset)
        if sort_form.is_valid():
            self.queryset = sorting(sort_form, self.queryset)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial_contact = {}
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(
                user=self.request.user, is_active=True).first()

            context['cart'] = cart
            phone = ''
            customer = Customer.objects.filter(user=self.request.user).first()
            if customer:
                phone = customer.phone
            initial_contact = {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'phone': phone
            }

        context['categories'] = Category.objects.all().select_related('parent')
        context['news'] = News.objects.get_news_limits()
        context['cart_info'] = self.cart_info
        context['sort_form'] = SortForm(initial=self.request.GET)
        context['search_form'] = SearchForm(initial=self.request.GET)
        context['contact_form'] = DiagnosticForm(initial=initial_contact)
        return context
