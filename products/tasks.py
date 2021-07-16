from datetime import datetime, timedelta

from celery import shared_task

from .models import Discount


@shared_task
def change_discount_status() -> None:
    today = datetime.today()
    discounts = Discount.objects.filter(
        is_active=True,
        date_finish__year__lte=today.year,
        date_finish__month__lte=today.month,
        date_finish__day__lte=today.day,
    ).all()
    for discount in discounts:
        discount.is_active=False
        discount.save()
    
