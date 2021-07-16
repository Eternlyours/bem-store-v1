from celery import shared_task
from datetime import datetime, timedelta
from .models import Order
from application import settings
from django.core.mail import get_connection, send_mail
from django.apps import apps


@shared_task
def remind_the_buyer_to_pay_for_the_order():
    today = datetime.today()
    date = today - timedelta(1)
    orders = Order.objects.filter(
        status=Order.STATUS_WAIT_BUY_ORDER,
        date_of_reg__year__lte=date.year,
        date_of_reg__month__lte=date.month,
        date_of_reg__day__lte=date.day
    ).all()
    connection = get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_ssl=settings.EMAIL_USE_SSL
    )
    for order in orders:
        send_mail(
            subject='Бензоэлектромастер приветствует вас!',
            message=f'Ваш заказ №{order.key} ожидает оплаты, завтра заказ удалится без возможности восстановления.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.customer.user.email],
            fail_silently=False
        )


@shared_task
def deletion_of_unpaid_orders():
    Cart = apps.get_model('cart', 'Cart')
    today = datetime.today()
    date = today - timedelta(2)
    orders = Order.objects.filter(
        status=Order.STATUS_WAIT_BUY_ORDER,
        date_of_reg__year__lte=date.year,
        date_of_reg__month__lte=date.month,
        date_of_reg__day__lte=date.day
    ).all()
    for order in orders:
        Cart.objects.filter(id=order.cart_id).delete()