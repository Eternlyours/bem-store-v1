from django.db import models
from products.models import Product


class WaitingList(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE, related_name='waiting', verbose_name=u'Товар')
    email = models.EmailField(verbose_name=u'Электронная почта')

    def __str__(self):
        return '{0} - {1}'.format(self.email, self.product)

    class Meta:
        verbose_name = 'Лист ожидания'
        verbose_name_plural = 'Листы ожидания'

