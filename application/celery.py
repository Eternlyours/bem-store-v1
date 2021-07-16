import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

app = Celery('application')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'clear-cart-everyday': {
        'task': 'cart.tasks.get_older_carts',
        'schedule': crontab(minute='*/5'),
    },
    'about_the_arrival_of_goods': {
        'task': 'waitinglist.tasks.notify_about_the_arrival_of_goods',
        'schedule': crontab(minute='*/5'),
    },
    'remind-the-buyer-to-pay-for-the-order': {
        'task': 'order.tasks.remind_the_buyer_to_pay_for_the_order',
        'schedule': crontab(minute='*/5'),
    },
    'deletion_of_unpaid_orders': {
        'task': 'order.tasks.deletion_of_unpaid_orders',
        'schedule': crontab(minute='*/5')
    },
    'change_discount_status': {
        'task': 'products.tasks.change_discount_status',
        'schedule': crontab(minute='*/5')
    },
}