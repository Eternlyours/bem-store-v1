from django.db import models
from django.conf import settings 
from django.utils.safestring import mark_safe


class Diagnostic(models.Model):
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        verbose_name='Почта',
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=255,
        verbose_name='Телефон',
        blank=True,
        null=True
    )
    tool = models.CharField(
        max_length=255,
        verbose_name=u'Инструмент',
        help_text='Производитель, модель, год...'
    )
    comment = models.TextField(
        verbose_name=u'Описание проблемы'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=u'Активность'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Создано')

    @property
    def comment_safe(self):
        return mark_safe(self.comment)
    comment_safe.fget.short_description = 'Комментарий'

    class Meta:
        verbose_name = 'Заявка клиента'
        verbose_name_plural = 'Заявки клиентов'


class FeedBack(Diagnostic):
    class Meta:
        proxy = True
        verbose_name = 'Рассылка посетителям'
        verbose_name_plural = 'Рассылки посетителям'