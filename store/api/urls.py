from django.urls import path

from .views import BrandListAPI, CategoryListAPI, ProductListAPI

urlpatterns = [
    path('products/', ProductListAPI.as_view()),
    path('brands/', BrandListAPI.as_view()),
    path('categories/', CategoryListAPI.as_view()),
]
