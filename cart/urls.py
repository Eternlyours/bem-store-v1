from django.urls import path
from .views import add_to_cart, delete_cart, CartView


urlpatterns = [
    path('products/detail/<slug:slug>/add-to-cart/', add_to_cart, name='add-to-cart'),
    path('products/detail/<slug:slug>/delete-item-cart/', delete_cart, name='delete-cart'),
    path('cart/', CartView.as_view(), name='cart'),
]