from application import settings
from celery import shared_task
from django.core.mail import get_connection, send_mail

from .models import WaitingList


@shared_task
def notify_about_the_arrival_of_goods():
    connection = get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_ssl=settings.EMAIL_USE_SSL
    )
    waiting_list = WaitingList.objects.all().select_related(
        'product'
    ).prefetch_related('product__brand')
    for item in waiting_list:
        if item.product.get_actual_quantity['total_quantity'] > 0:
            message = 'Доброго времени суток! Товар из листа ожидания - {0} {1} {2} - появился в продаже!'.format(
                    item.product.brand.name, item.product.model, item.product.article)
            send_mail(
                subject='Поступление товара',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[item.email],
                fail_silently=False
            )
            item.delete()

