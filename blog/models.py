from django.db import models
from .managers import NewsManager
from django.conf import settings
from unidecode import unidecode
from django.template.defaultfilters import slugify

import uuid


class NewsViews(models.Model):
    post = models.ForeignKey(
        'News', on_delete=models.CASCADE, related_name='views_count', verbose_name=u'Публикация')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=u'Пользователь')

    def __str__(self):
        return '{0} {1}'.format(self.post.title, self.user.username)


class News(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(verbose_name=u'Семантический URL',
                            unique=True, blank=True, null=True, max_length=500)
    title = models.CharField(verbose_name=u'Заголовок', max_length=150)
    body = models.TextField(verbose_name=u'Тело новости', max_length=5500)
    date = models.DateTimeField(
        verbose_name=u'Дата создания',
        auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name=u'Отображать')

    objects = NewsManager()

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(unidecode(self.title))
            duplicate = News.objects.filter(slug=slug)
            if duplicate.exists():
                self.slug = '%s - %s' % (slug, uuid.uuid4().hex)
            else:
                self.slug = slug
        return super().save(*args, **kwargs)

    @property
    def get_views(self):
        return NewsViews.objects.filter(post=self).count()
    get_views.fget.short_description = 'Просмотров'


class Service(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(verbose_name=u'Семантический URL',
                            unique=True, blank=True, null=True, max_length=500)
    title = models.CharField(verbose_name=u'Заголовок', max_length=150)
    body = models.TextField(verbose_name=u'Тело новости', max_length=5500)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(unidecode(self.title))
            duplicate = self.__class__.objects.filter(slug=slug)
            if duplicate.exists():
                self.slug = '%s - %s' % (slug, uuid.uuid4().hex)
            else:
                self.slug = slug
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Блог компании'
        verbose_name_plural = 'Блог компании'
