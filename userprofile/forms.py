from django import forms
from store.forms import BaseForm


class UserCustomForm(BaseForm, forms.Form):
    username = forms.CharField(max_length=255, label='Имя пользователя')
    first_name = forms.CharField(max_length=255, label='Имя', required=False)
    last_name = forms.CharField(max_length=255, label='Фамилия', required=False)
    email = forms.CharField(widget=forms.EmailInput(),
                            label='Электронная почта', required=False)
    new_password = forms.CharField(
        widget=forms.PasswordInput(), label='Новый пароль', required=False)
    old_password = forms.CharField(label='Старый пароль', required=False,
                                       widget=forms.PasswordInput)
    address = forms.CharField(max_length=255, label='Адрес', required=False)
    phone = forms.CharField(max_length=11, label='Телефон', required=False)
