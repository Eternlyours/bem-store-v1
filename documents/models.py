from django.db import models
from products.models import Product


class DocumentProductQuantity(models.Model):
    COMING_CHOICES = '+'
    SPENDING_CHOICES = '-'

    CHOICES = (
        (COMING_CHOICES, 'Приход'),
        (SPENDING_CHOICES, 'Расход')
    )

    product = models.ForeignKey(
        Product, related_name='document_quantity', on_delete=models.CASCADE, verbose_name='Товар')
    actual_date = models.DateTimeField(
        verbose_name='Актуальная дата', null=True, blank=True)
    actual_date_doc = models.DateTimeField(
        verbose_name='Дата проведения документа', auto_now_add=True)
    quantity = models.PositiveIntegerField(
        verbose_name='Количество', null=True, blank=True)
    is_return = models.BooleanField(verbose_name='Возврат', default=False)
    price = models.DecimalField(
        verbose_name='Стоимость', max_digits=15, decimal_places=2, null=True, blank=True)
    type = models.CharField(
        choices=CHOICES, verbose_name='Тип движения', max_length=255)

    def __str__(self):
        return '{0} ({1}) {2} - {3}'.format(self.product, self.type, self.actual_date, self.quantity)

    class Meta:
        verbose_name = 'Документ учёта количества продуктов'
        verbose_name_plural = 'Документы учёта количества продуктов'


class DocumentProductPrice(models.Model):
    product = models.ForeignKey(
        Product, related_name='document_price', on_delete=models.CASCADE, verbose_name='Товар')
    actual_date = models.DateTimeField(verbose_name='Актуальная дата')
    price = models.DecimalField(
        verbose_name='Стоимость', max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.product, self.price, self.actual_date)

    class Meta:
        verbose_name = 'Регистр цен'
        verbose_name_plural = 'Регистры цен'