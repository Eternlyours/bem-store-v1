from django.template.defaultfilters import lower
from blog.models import *
from cart.utils import CartMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.defaulttags import register
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView
from products.forms import FilterForm, SortForm
from products.models import *
from products.models import Comment
from waitinglist.forms import WaitingListForm
from waitinglist.models import WaitingList

from store.utils import BaseFormView, BaseListView, filtering, sorting

from .forms import CommentForm, SearchForm
from .models import *


class TestView(BaseListView, ListView):
    template_name = 'temp.html'
    queryset = Product.objects.get_products()


@register.filter
def morphy():
    pass


def not_found(request):
    raise Http404('Error')


class CatalogListView(BaseListView, BaseFormView, ListView):
    template_name = 'catalog.html'
    queryset = Product.objects.get_products()

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
        context['title'] = 'Каталог'
        return context


class SearchListView(BaseListView, BaseFormView, ListView):
    template_name = 'catalog.html'
    queryset = Product.objects.get_products()

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        filter_form = FilterForm(self.request.GET)
        sort_form = SortForm(self.request.GET)
        if form.is_valid():
            from django.db.models import CharField
            from django.db.models.functions import Lower

            CharField.register_lookup(Lower)

            param = form.cleaned_data['q']
            if not param:
                param = self.request.GET.get('q')
            self.queryset = self.queryset.filter(
                Q(model__icontains=lower(param)) 
                | Q(brand__name__icontains=lower(param))
                | Q(category__name__icontains=lower(param))
                | Q(brand__name__iexact=lower(param))
                | Q(category__name__iexact=lower(param))
                | Q(brand__name__lower=lower(param))
                | Q(category__name__lower=lower(param)))
            if filter_form.is_valid():
                self.queryset = filtering(filter_form, self.queryset)
            if sort_form.is_valid():
                self.queryset = sorting(sort_form, self.queryset)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')
        context['breadcrumbs_search'] = ['Поиск', context['q']]
        context['title'] = f'Поиск | {context["q"]}'
        return context


class ServiceListView(BaseListView, ListView):
    template_name = 'blogservice.html'
    queryset = Service.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Блог компании'
        return context


class ServiceDetailView(BaseListView, DetailView):
    template_name = 'item-blogservice.html'
    queryset = Service.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        context['title'] = object.title
        return context


class NewsListView(BaseListView, ListView):
    template_name = 'blog.html'
    queryset = News.objects.get_news()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новости'
        return context


class NewsDetailView(BaseListView, DetailView):
    template_name = 'item-blog.html'
    queryset = News.objects.get_news()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.object = self.get_object()
            context = super().get_context_data(**kwargs)
            item, created = NewsViews.objects.get_or_create(
                post=self.object,
                user=request.user
            )
            context['title'] = self.object.title
            return render(request, self.template_name, context)
        return super().get(request, *args, **kwargs)


def custom_404(request):
    return render(request, template_name='404page.html', status=404)


class DiscountListView(BaseListView, ListView):
    template_name = 'discounts.html'
    queryset = Discount.objects.all().filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Скидки'
        return context


class BaseView(BaseListView, BaseFormView, ListView):
    template_name = 'main.html'
    queryset = Product.objects.get_products()

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
        products = Product.objects.get_products()
        context['popular'] = products.order_by('-popular')[:20]
        context['title'] = 'Главная'
        return context


class ProductCategoryListView(BaseListView, BaseFormView, ListView):
    template_name = 'catalog.html'
    queryset = Product.objects.get_products()

    def get_queryset(self):
        queryset = self.queryset.filter(Q(
            category__parent__slug=self.kwargs['slug'].split('/')[-1])
            | Q(category__slug=self.kwargs['slug'].split('/')[-1]))
        form = FilterForm(self.request.GET)
        sort_form = SortForm(self.request.GET)
        if form.is_valid():
            queryset = filtering(form, queryset)
        if sort_form.is_valid():
            queryset = sorting(sort_form, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = Category.objects.get(
            slug=self.kwargs['slug'].split('/')[-1])
        context['breadcrumb_item'] = object
        context['title'] = object
        return context


class ProductFilterListView(BaseListView, BaseFormView, ListView):
    template_name = 'catalog.html'
    queryset = Product.objects.get_products()

    def get_queryset(self):
        form = FilterForm(self.request.GET)
        sort_form = SortForm(self.request.GET)
        if form.is_valid():
            self.queryset = filtering(form, self.queryset)
        if sort_form.is_valid():
            self.queryset = sorting(sort_form, self.queryset)
        return self.queryset


class ProductDetailView(BaseListView, DetailView):
    template_name = 'item-product.html'
    queryset = Product.objects.get_products()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}
        comments = Comment.objects.filter(product=self.object).all().select_related(
            'user').values('user__first_name', 'user__last_name', 'user__username', 'body', 'date', 'user')
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if self.request.user.is_authenticated:
            initial = {'email': self.request.user.email}
        context['waiting_form'] = WaitingListForm(initial=initial)
        context['comment_form'] = CommentForm()
        context['page_obj'] = page_obj
        product = self.get_object()
        context['title'] = f'{product.brand.name} {product.model}'
        context['choice_list'] = ['комментарий', 'комментария', 'комментариев']
        context['choice_list_p'] = ['штука', 'штуки', 'штук']
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        self.object = self.get_object()
        form_waitinglist = WaitingListForm(request.POST)
        rate = self.request.POST.get('rating')
        if rate:
            if request.user.is_authenticated:
                user_action, created = ProductUserAction.objects.get_or_create(
                    user=request.user, product=self.object
                )
                user_action.rate = rate
                user_action.save()
            else:
                messages.error(
                    request, 'Анонимные пользователи не могут давать оценки')
        if form.is_valid():
            if request.user.is_authenticated:
                body = form.cleaned_data['body']
                content_type = Comment(
                    product=self.object, body=body, user=request.user)
                content_type.save()
            else:
                messages.error(
                    request, 'Анонимные пользователи не могут оставлять комментарии')
        if form_waitinglist.is_valid():
            email = form_waitinglist.cleaned_data['email']
            WaitingList.objects.get_or_create(email=email, product=self.object)
            messages.success(
                request, 'Товар добавлен в лист ожидания!'
            )
            return HttpResponseRedirect(self.request.path_info)
        return HttpResponseRedirect(self.request.path_info)


@login_required(login_url='login')
def delete(request):

    return HttpResponseRedirect(reverse('home'))


class AboutView(BaseListView, TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{'title':'О нас'})
