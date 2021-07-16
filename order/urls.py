from django.urls import path
from .views import OrderView, SuccessOrderView, removeOrder
from authenticator.decorators import check_recaptcha


urlpatterns = [
    path('checkout/', check_recaptcha(OrderView.as_view()), name='checkout'),
    path('checkout/success/', SuccessOrderView.as_view(), name='success-order'),
    path('checkout/delete/<id>/', removeOrder, name='checkout-delete'),
]