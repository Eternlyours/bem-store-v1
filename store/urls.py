from django.conf.urls import url
from django.urls import include, path
from products.views import add_to_favorite_list
from .api import urls
from .views import (AboutView, BaseView, DiscountListView, NewsDetailView, NewsListView, ServiceDetailView,
                    ProductCategoryListView, ProductDetailView, ServiceListView, 
                    ProductFilterListView, SearchListView, TestView, delete, CatalogListView)

urlpatterns = [
    url(r'^$', BaseView.as_view(), name='home'),
    path('catalog/', CatalogListView.as_view(), name='catalog'),
    path('catalog/search/', SearchListView.as_view(), name='search'),
    url(r'^catalog/(?P<slug>[\w\d_/-]+)/$',
        ProductCategoryListView.as_view(), name='product-category'),
    path('products/detail/<slug>/',
         ProductDetailView.as_view(), name='detail-product'),
    path('products/detail/<slug>/action-to-favorite/',
         add_to_favorite_list, name='product-add-favorite'),
    url(r'^blog/news/$', NewsListView.as_view(), name='news-list'),
    path(r'blog/news/detail/<slug>', NewsDetailView.as_view(), name='detail-news'),
    path('blog/service/', ServiceListView.as_view(), name='service-list'),
    path('blog/service/detail/<slug>', ServiceDetailView.as_view(), name='service-detail'),
    path('cart/delete/', delete, name='delete'),
    path('api/', include(urls)),
    path('temp/', TestView.as_view()),
    path('catalog/filter', ProductFilterListView.as_view(), name='filtering'),
    path('about-us/', AboutView.as_view(), name='about-us'),
    path('discounts/', DiscountListView.as_view(), name='discounts'),
]
