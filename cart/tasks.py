from datetime import datetime, timedelta

from celery import shared_task

from .models import Cart


@shared_task
def get_older_carts():
    today = datetime.today()
    date = today - timedelta(3)
    queryset = Cart.objects.filter(
        is_active=True,
        updated_at__year__lte=date.year,
        updated_at__month__lte=date.month,
        updated_at__day__lte=date.day).all().delete()
    return True
