from django.db import models
from django.db.models import Count


class NewsManager(models.Manager):

    def get_news(self):
        return self.order_by('-date').annotate(views=Count('views_count')).all()

    def get_news_limits(self):
        return self.filter(active=True).order_by('-date').all()[:3]