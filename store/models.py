from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from unidecode import unidecode
from django.apps import apps


class Category(MPTTModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name=u'Название', max_length=50)
    slug = models.SlugField(verbose_name=u'Семантический URL',
                            max_length=150, unique=True)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name=u'Основная категория',
        null=True,
        blank=True, related_name='child')
    icon = models.FileField(verbose_name=u'Иконка',
                            upload_to='uploads/icons/', null=True, blank=True)

    def get_absolute_url(self):
        path = '/'.join([x['slug']
                         for x in self.get_ancestors(include_self=True).values()])
        kwargs = {
            'slug': path
        }

        return reverse('product-category', kwargs=kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['name']


class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name=u'Название', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'


class Customer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='customer',
                             on_delete=models.CASCADE, verbose_name=u'Пользователь')
    phone = models.CharField(
        max_length=11, verbose_name=u'Телефон', null=True, blank=True)
    address = models.CharField(
        max_length=255, verbose_name=u'Адрес', null=True, blank=True)

    def __str__(self):
        return '{0} - {1}'.format(str(self.user), str(self.phone))

    class Meta:
        verbose_name = u'Покупателя'
        verbose_name_plural = u'Покупатели'

