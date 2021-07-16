from django.urls import path
from .views import PaymentView


urlpatterns = [
    path('checkout/payment/<id>/', PaymentView.as_view(), name='payment'),
]