from django import forms
from django.core.cache import cache
from django.template.defaultfilters import slugify
from store.forms import BaseForm, get_tuple_brand, get_tuple_category
from unidecode import unidecode

from .models import ProductCharacteristic


class SortForm(BaseForm):
    PRICE_CHOICES = (('price_discount', 'Цена по возрастанию'),
                     ('-price_discount', 'Цена по убыванию'))
    RATE_CHOICES = (('avg', 'Оценка по возрастанию'),
                    ('-avg', 'Оценка по убыванию'))
    blank_choice = (('', '--- Всё ---'),)
    sort_price = forms.ChoiceField(
        choices=blank_choice+PRICE_CHOICES,
        label='По цене',
        required=False
    )
    sort_rate = forms.ChoiceField(
        choices=blank_choice+RATE_CHOICES,
        label='По оценке',
        required=False
    )


class FilterForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update(
            {'class': 'list-unstyled ml-3', 'id': 'category-toggle'})

        fields_qs = ProductCharacteristic.objects.values(
            'name', 'unit').distinct()
        for field in fields_qs:
            name = slugify(unidecode(field['name']))
            field_unit = field['unit']
            if field_unit in ['Кг', 'Вт', 'См', 'кВт']:
                _max = 'max_{0}'.format(name)
                _min = 'min_{0}'.format(name)

                self.fields[_max] = forms.FloatField(
                    label='Maкс. {0}'.format(str.lower(field['name'])),
                    required=False, widget=forms.NumberInput)
                self.fields[_min] = forms.FloatField(
                    label='Мин. {0}'.format(str.lower(field['name'])),
                    required=False, widget=forms.NumberInput)
                self.fields[_max].widget.attrs.update(
                    {'class': 'form-control'})
                self.fields[_min].widget.attrs.update(
                    {'class': 'form-control'})
            else:
                CHOICES = list(ProductCharacteristic.objects.filter(
                    name=field['name']).values_list('text_value', 'text_value').distinct())
                if len(CHOICES) <= 1:
                    pass
                else:
                    self.fields[name] = forms.MultipleChoiceField(
                        choices=CHOICES,
                        widget=forms.CheckboxSelectMultiple,
                        required=False,
                        label=field['name']
                    )
                    self.fields[name].widget.attrs.update(
                        {'class': 'list-unstyled ml-3'}
                    )

    choices_category = get_tuple_category()
    choices_brand = get_tuple_brand()
    blank_choice = (('', '--- Всё ---'),)
    category = forms.MultipleChoiceField(
        choices=choices_category,
        required=False,
        label='Категория',
        widget=forms.CheckboxSelectMultiple
    )
    quantity = forms.ChoiceField(
        choices=blank_choice+(
            ('in-stock', 'В наличии'),
            ('out-of-stock', 'Нет в наличии')
        ),
        required=False,
        label='Наличие'
    )
    brand = forms.ChoiceField(choices=blank_choice +
                              choices_brand, label='Марка', required=False)
    max_price = forms.DecimalField(label='Макс. цена', required=False, decimal_places=2, widget=forms.NumberInput)
    min_price = forms.DecimalField(label='Мин. цена', required=False, decimal_places=2, widget=forms.NumberInput)
