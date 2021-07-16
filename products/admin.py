from datetime import datetime

from ckeditor.widgets import CKEditorWidget
from django.apps import apps
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.html import mark_safe
from documents.models import DocumentProductPrice, DocumentProductQuantity
from import_export import fields, resources
from django.db.models.query import EmptyQuerySet
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from .models import (Comment, Discount, Photo, Product, ProductCharacteristic,
                     ProductUserAction)


class CaracteristicsAdmin(admin.TabularInline):
    model = ProductCharacteristic


class BaseInlineAddOnlyFormSet(BaseInlineFormSet):

    def get_queryset(self):
        return Product.objects.none()


class DocumentQuantitInline(admin.TabularInline):
    model = DocumentProductQuantity
    formset = inlineformset_factory(Product, DocumentProductQuantity, exclude=(
        'price', 'is_return', ), formset=BaseInlineAddOnlyFormSet, fk_name='product')
    extra = 1
    max_num = 1
    exclude=('price', 'is_return', )


class DocumentPriceInline(admin.TabularInline):
    model = DocumentProductPrice
    formset = inlineformset_factory(
        Product, DocumentProductPrice, fields='__all__', 
        formset=BaseInlineAddOnlyFormSet, fk_name='product')
    extra = 1
    max_num = 1


class PhotoAdmin(admin.TabularInline):

    def tag_image(self, obj):
        return mark_safe('<img src="{0}" width="150px" height="100px" style="object-fit:cover;" />'.format(obj.image.url))
    list_display = ['tag_image', ]
    readonly_fields = ['tag_image']
    tag_image.short_description = 'Картинка'
    model = Photo


class ProductResources(resources.ModelResource):
    Brand = apps.get_model('store', 'Brand')
    Category = apps.get_model('store', 'Category')

    article = fields.Field(
        attribute='article',
        column_name='Артикул'
    )

    model = fields.Field(
        attribute='model',
        column_name='Модель'
    )

    price = fields.Field(
        attribute='price',
        column_name='Цена'
    )

    description = fields.Field(
        attribute='description',
        column_name='Описание'
    )

    type_buy = fields.Field(
        attribute='type_buy',
        column_name='Вид покупки'
    )

    delivery = fields.Field(
        attribute='delivery',
        column_name='Доставка'
    )

    brand = fields.Field(
        column_name='Производитель',
        attribute='brand',
        widget=ForeignKeyWidget(Brand, 'name')
    )

    category = fields.Field(
        column_name='Категория',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        return super().before_import(dataset, using_transactions, dry_run, **kwargs)

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        excluded_fields = ['Артикул', 'Модель', 'Производитель', 'Вид покупки',
                           'Количество', 'Категория', 'Цена', 'Дата', 'Описание']
        for row in dataset.dict:
            product = Product.objects.get(article=row['Артикул'])

            date_str_temp = str(row['Дата'])
            price = row['Цена']
            quantity = row['Количество']

            try:
                obj = datetime.strptime(date_str_temp, '%Y-%m-%d %H:%M:%S')
            except:
                obj = datetime.strptime(date_str_temp, '%d.%m.%Y')
            date_str = datetime.strftime(obj, '%Y-%m-%d')

            document_q, created = DocumentProductQuantity.objects.get_or_create(
                product=product,
                actual_date=date_str
            )

            if created:
                document_q.quantity = quantity
                document_q.type = DocumentProductQuantity.COMING_CHOICES

            document_p, created = DocumentProductPrice.objects.get_or_create(
                product=product,
                actual_date=date_str
            )

            if created:
                document_p.price = price

            document_q.save()
            document_p.save()

            for col in row:
                if col not in excluded_fields:
                    if row[col]:
                        value = row[col].split('|')
                        try:
                            ProductCharacteristic.objects.get_or_create(
                                product=product,
                                decimal_value=float(value[0]) or int(value[0]),
                                unit=value[1],
                                name=col
                            )
                        except:
                            if len(value) == 1:
                                ProductCharacteristic.objects.get_or_create(
                                    product=product,
                                    text_value=value[0],
                                    name=col
                                )
                            else:
                                ProductCharacteristic.objects.get_or_create(
                                    product=product,
                                    text_value=value[0],
                                    name=col,
                                    unit=value[1]
                                )
        return super().after_import(dataset, result, using_transactions, dry_run, **kwargs)

    class Meta:
        model = Product
        import_id_fields = ('article', )
        fields = ('article', 'model', 'category',
                  'brand', 'description', 'delivery', 'type_buy')
        export_order = ('article', 'model', 'category',
                        'brand', 'description', 'delivery', 'type_buy')


class ProductAdmin(ImportExportModelAdmin):
    fields = ('slug', 'active', 'article', 'model', 'rating', 'actual_quantity_for_admin', 'actual_price_for_admin', 'actual_price_with_discount_for_admin', 'brand', 'category',
              'delivery', 'type_buy', 'description')
    list_display = ('id', 'article', 'model', 'brand', 'category', 'slug')
    list_display_links = ('brand', 'article', 'model', 'slug')
    search_fields = ('brand__name', 'model', 'description', 'slug')
    list_filter = ('brand', 'category', 'delivery', 'type_buy')
    readonly_fields = (
        'rating', 'slug', 'actual_quantity_for_admin', 'actual_price_for_admin', 'actual_price_with_discount_for_admin')
    inlines = (DocumentPriceInline, DocumentQuantitInline,
               CaracteristicsAdmin, PhotoAdmin)
    # inlines = (CaracteristicsAdmin, PhotoAdmin)

    formfield_overrides = {
        models.TextField: {
            'widget': CKEditorWidget(config_name='product_ckeditor')
        }
    }

    resource_class = ProductResources


class PhotoAdminDef(admin.ModelAdmin):
    model = Photo


class DiscountAdmin(admin.ModelAdmin):
    fields = ('name', 'amount_discount', 'products',
              'is_active', 'date_start', 'date_finish',)
    list_display = ('name', 'amount_discount', 'is_active',)
    list_display_links = ('name',)
    readonly_fields = ('is_active', 'date_start', )


admin.site.register(Product, ProductAdmin)
# admin.site.register(Photo, PhotoAdminDef)
# admin.site.register(ProductUserAction)
# admin.site.register(ProductCharacteristic)
admin.site.register(Discount, DiscountAdmin)
# admin.site.register(Comment)
