from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Order
from store.forms import BaseForm
from django.core.validators import EmailValidator


class CustomOrderForm(BaseForm, forms.Form):
    blank_choice = (('', '  ---  '),)
    first_name = forms.CharField(max_length=255, label='Имя', required=True)
    last_name = forms.CharField(max_length=255, label='Фамилия', required=True)
    email = forms.EmailField(label='Электронная почта',
                             required=True, validators=[EmailValidator])
    address = forms.CharField(
        max_length=255, label='Адрес', help_text='Обязательно укажите город!', required=True)
    phone = forms.CharField(max_length=11, label='Телефон',
                            help_text='Укажите свой реальный номер по которому менежер сможет с вами связаться!', required=True)
    type_buy = forms.ChoiceField(
        choices=blank_choice+Order.TYPE_BUY_CHOICES, label='Способ оплаты', required=True)
    type_delivery = forms.ChoiceField(
        choices=blank_choice+Order.TYPE_DELIVERY_CHOICES, label='Способ доставки', required=True)
    comment = forms.CharField(
        widget=CKEditorWidget(config_name='comment_order_ckeditor'),
        required=False,
        label=u'Комментарий')

    type_buy_hidden = forms.CharField(widget=forms.HiddenInput(), required=True)
    type_delivery_hidden = forms.CharField(widget=forms.HiddenInput(), required=True)

    def clean(self):
        cleaned_data = super().clean()
        type_buy = cleaned_data.get('type_buy', '')
        type_buy_hidden = cleaned_data.get('type_buy_hidden', '')
        if type_buy_hidden and type_buy:
            if int(type_buy_hidden) > 0 and type_buy == Order.TYPE_CASH_PAYMENT:
                self.add_error('type_buy', 'Покупка под заказ осуществляется после полной предоплаты!')
                # raise forms.ValidationError(
                #     'Покупка под заказ осуществляется после полной предоплаты!')

        type_delivery = cleaned_data.get('type_delivery', '')
        type_delivery_hidden = cleaned_data.get('type_delivery_hidden', '')
        if type_delivery_hidden and type_delivery:
            if int(type_delivery_hidden) > 0 and type_delivery == Order.TYPE_DELIVERY_DELIVERY:
                self.add_error('type_delivery', 'Пожалуйста, выберите вариант доставки соответствующий с условиями заказа')
                # raise forms.ValidationError(
                #     'Пожалуйста, выберите вариант доставки соответствующий с условиями заказа')
        return cleaned_data
