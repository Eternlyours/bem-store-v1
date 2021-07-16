import uuid
import random

from django.core.checks import messages

from application import settings
from cart.models import Cart, ItemCart
from django.apps import apps
from django.core.mail import get_connection, send_mail
from django.db import models
from django.utils.safestring import mark_safe
from store.models import Customer


def random_key_order():
    return str(random.randint(1000000000, 9999999999))


class Order(models.Model):
    STATUS_NEW_ORDER = 'new_order'
    STATUS_PROGRESS_ORDER = 'assembly'
    STATUS_WAIT_BUY_ORDER = 'wait_buy'
    STATUS_READY_ISSUE_ORDER = 'ready'
    STATUS_ISSUED_ORDER = 'issued'
    STATUS_CANCELED_ORDER = 'canceled'

    STATUS_ORDER_CHOICES = (
        (STATUS_NEW_ORDER, 'Новый заказ'),
        (STATUS_WAIT_BUY_ORDER, 'В ожидании оплаты'),
        (STATUS_PROGRESS_ORDER, 'В процессе сборки'),
        (STATUS_READY_ISSUE_ORDER, 'Готов к выдачи'),
        (STATUS_ISSUED_ORDER, 'Выдан'),
        (STATUS_CANCELED_ORDER, 'Отменён'),
    )

    TYPE_PICKUP_DELIVERY = 'pickup'
    TYPE_DELIVERY_DELIVERY = 'delivery'

    TYPE_DELIVERY_CHOICES = (
        (TYPE_PICKUP_DELIVERY, 'Самовывоз'),
        (TYPE_DELIVERY_DELIVERY, 'Доставка'),
    )

    TYPE_CARD_PAYMENT = 'card'
    TYPE_CASH_PAYMENT = 'cash'

    TYPE_BUY_CHOICES = (
        (TYPE_CARD_PAYMENT, 'Оплата картой - онлайн'),
        (TYPE_CASH_PAYMENT, 'Оплата наличными'),
    )

    id = models.SlugField(default=uuid.uuid4, editable=False,
                          primary_key=True, unique=True)
    key = models.CharField(max_length=10, verbose_name='Код заказа',
                           default=random_key_order, unique=True)
    is_confirm = models.BooleanField(verbose_name='Подтвержден', default=False)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, verbose_name=u'Корзина', related_name='order')
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='order')
    date = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Дата создания заказа')
    date_of_reg = models.DateTimeField(verbose_name=u'Дата оформления заказа',
                                       null=True, blank=True
                                       )
    amount = models.FloatField(verbose_name=u'Цена', default=0)
    status = models.CharField(default=STATUS_NEW_ORDER,
                              choices=STATUS_ORDER_CHOICES, verbose_name=u'Статус заказа', max_length=255, null=True, blank=True)
    buy = models.CharField(choices=TYPE_BUY_CHOICES,
                           verbose_name=u'Вид оплаты', max_length=255, null=True, blank=True)
    type_delivery = models.CharField(
        choices=TYPE_DELIVERY_CHOICES, verbose_name=u'Вид доставки', max_length=255, null=True, blank=True)
    comment = models.TextField(
        verbose_name=u'Комментарий', null=True, blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.id, self.customer.user.username)

    @property
    def comment_safe(self):
        return mark_safe(self.comment)
    comment_safe.fget.short_description = 'Комментарий'

    def save(self, *args, **kwargs):
        DocumentProductQuantity = apps.get_model(
            'documents', 'DocumentProductQuantity')
        if self.status in self.STATUS_PROGRESS_ORDER:
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=settings.EMAIL_USE_SSL
            )
            message = f'''
                {self.customer.user.first_name} {self.customer.user.last_name} здравствуйте!\n
                Был оформлен новый заказ №{self.key}\n
                На сумму {self.amount}\n
                Следите за статусом заказа на сайте
            '''
            send_mail(
                subject=f'Был оформлен новый заказ №{self.key}',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.customer.user.email],
                fail_silently=False
            )
        if self.status and not self.status in self.STATUS_NEW_ORDER:
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=settings.EMAIL_USE_SSL
            )
            message = f'''
                Уважаемый {self.customer.user.first_name} {self.customer.user.last_name}, 
                ваш заказ №{self.key} сменил статус на: {self.get_status_display()}
            '''
            send_mail(
                subject='Смена статуса заказа',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.customer.user.email],
                fail_silently=False
            )
        if self.status == self.STATUS_PROGRESS_ORDER:
            cart = Cart.objects.get(id=self.cart_id)
            items = ItemCart.objects.get_items(cart)
            for item in items:
                DocumentProductQuantity.objects.create(
                    product=item.product,
                    quantity=item.quantity,
                    price=item.total_price_discount,
                    type=DocumentProductQuantity.SPENDING_CHOICES
                )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


# def confirm_key():
#     return str(random.randint(100000, 999999))


# class OrderConfirmed(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     key = models.CharField(max_length=8, default=confirm_key())