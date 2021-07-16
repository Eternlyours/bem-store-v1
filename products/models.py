from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.db import models
from django.db.models.fields import DecimalField
from django.db.utils import cached_property
from django.template.defaultfilters import slugify
from mptt.models import TreeForeignKey
from store.managers import ProductManager
from store.models import Brand, Category
from django.db.models import Value, IntegerField
from django.db.models.functions import Coalesce
from unidecode import unidecode
from django.apps import apps
from django.db.models.aggregates import Avg, Sum
from django.db.models.expressions import ExpressionWrapper, OuterRef
from django.db.models.query import F, Q


class Product(models.Model):
    UNDER_THE_ORDER = 'Под заказ'
    IN_THE_SHOP = 'В магазине'

    CHOICES = (
        (UNDER_THE_ORDER, 'Под заказ (14 дней)'),
        (IN_THE_SHOP, 'Покупка в магазине')
    )

    id = models.AutoField(primary_key=True)
    slug = models.SlugField(verbose_name=u'Семантический URL',
                            max_length=150, unique=True)
    model = models.CharField(verbose_name=u'Модель', max_length=50)
    article = models.CharField(
        verbose_name=u'Артикул',
        max_length=35,
        unique=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        verbose_name=u'Производитель')
    category = TreeForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=u'Категория')
    description = models.TextField(
        verbose_name=u'Описание',
        max_length=3500,
        blank=True,
        null=True)
    active = models.BooleanField(verbose_name=u'Отображать', default=True)

    type_buy = models.CharField(verbose_name=u'Вид покупки',
                                choices=CHOICES, max_length=255)
    delivery = models.BooleanField(
        verbose_name=u'Доставка', default=False)

    objects = ProductManager()

    def __str__(self):
        return '{0} - {1}'.format(self.article, self.model)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        if not self.slug:
            raw_slug = '%s %s %s' % (self.brand.name, self.model, self.article)
            self.slug = slugify(unidecode(raw_slug))
        return super().save(*args, **kwargs)

    @cached_property
    def rating(self):
        obj = ProductUserAction.objects.filter(
            product=self).aggregate(Avg('rate'))['rate__avg']
        if not obj:
            obj = 0
        rate = '%.2f' % obj
        return rate
    rating.short_description = 'Оценка'

    @cached_property
    def actual_price_with_discount_for_admin(self):
        price = self.actual_price_for_admin
        obj = Product.objects.filter(id=self.id).prefetch_related(
            'discount').aggregate(
                discount=Coalesce(
                    Sum('discount__amount_discount', filter=Q(
                        discount__amount_discount__gt=0, discount__is_active=True)),
                    Value(0)
                )
        )
        price = price - (price * obj['discount']) / Decimal(100)
        return Decimal(price)
    actual_price_with_discount_for_admin.short_description = 'Стоимость с учётом скидок'

    @cached_property
    def actual_quantity_for_admin(self):
        obj = self.get_actual_quantity
        return obj['total_quantity']
    actual_quantity_for_admin.short_description = 'Количесто товаров'

    @cached_property
    def actual_price_for_admin(self):
        DocumentProductPrice = apps.get_model(
            'documents', 'DocumentProductPrice')
        obj = DocumentProductPrice.objects.filter(
            product=self).order_by(
            '-actual_date').values('price')[:1].get()
        return obj['price']
    actual_price_for_admin.short_description = 'Стоимость товара'

    @cached_property
    def get_actual_quantity(self):
        DocumentProductQuantity = apps.get_model(
            'documents', 'DocumentProductQuantity')
        minus = Coalesce(
            Sum('quantity', filter=Q(type=DocumentProductQuantity.SPENDING_CHOICES)),
            Value(0)
        )
        plus = Coalesce(
            Sum('quantity', filter=Q(type=DocumentProductQuantity.COMING_CHOICES)),
            Value(0)
        )
        obj = DocumentProductQuantity.objects.filter(
            product=self
        ).all().values('product').aggregate(
            plus=plus,
            minus=minus,
            total_quantity=plus-minus
        )
        return obj
    get_actual_quantity.short_description = 'Количество'


class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(
        verbose_name=u'Картинка',
        upload_to='uploads/products/%y/%m/%d/')
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=u'Продукт',
        related_name='images')

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class ProductCharacteristic(models.Model):
    CHOICES = [
        ('Кг', 'Кг'),
        ('Вт', 'Вт'),
        ('кВт', 'кВт'),
        ('Шт', 'Шт'),
        ('См', 'См'),
        ('М', 'М'),
        ('мм', 'мм'),
        ('м2', 'м2'),
        ('Л', 'Л'),
        ('км\ч', 'км\ч'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='characteristic')
    # product = models.ManyToManyField(Product, related_name='characteristic', verbose_name=u'Продукт')
    name = models.CharField(
        max_length=100, verbose_name=u'Характеристика', blank=True, null=True)
    decimal_value = models.DecimalField(
        max_digits=19, decimal_places=10, verbose_name=u'Числовое значение', blank=True, null=True)
    text_value = models.CharField(
        max_length=100, verbose_name=u'Текстовое значение', blank=True, null=True)
    unit = models.CharField(choices=CHOICES, blank=True,
                            null=True, max_length=255)

    def __str__(self):
        return '{0} - {1}'.format(self.product.slug, self.name)

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'


class ProductUserAction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='action', verbose_name=u'Пользователь')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE, related_name='action', verbose_name=u'Продукт')
    rate = models.PositiveIntegerField(verbose_name=u'Оценка', default=0)
    favorite = models.BooleanField(
        verbose_name=u'Понравившийся', default=False)

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.product)

    class Meta:
        verbose_name = 'Отношение Пользователь - Продукт'
        verbose_name_plural = 'Отношения Пользователь - Продукт'


class Discount(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование скидки')
    products = models.ManyToManyField(Product, related_name='discount',
                                      verbose_name=u'Продукты на которые распространяется скидка')
    amount_discount = models.IntegerField(verbose_name=u'Размер скидки в %', validators=[
                                          MaxValueValidator(100), MinValueValidator(0)])
    is_active = models.BooleanField(verbose_name=u'Активность', default=True)
    date_start = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Дата начала действия скидки')
    date_finish = models.DateTimeField(
        verbose_name=u'Дата окончания действия скидки'
    )

    def __str__(self):
        return str(self.amount_discount)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='comment', verbose_name=u'Автор')
    body = models.TextField(verbose_name=u'Комментарий')
    date = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Дата создания')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='comment', verbose_name=u'Продукт')

    def __str__(self):
        return self.body

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-date']
