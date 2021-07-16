from django.contrib.auth import forms, models
from django import forms as form
from store.forms import BaseForm


class LoginForm(BaseForm, forms.AuthenticationForm, form.ModelForm):
    username = form.CharField(label='Логин', required=True)
    password = form.CharField(label='Пароль', widget=form.PasswordInput, required=True)

    class Meta:
        model = models.User
        fields = (
            'username',
            'password'
        )


class SigninForm(BaseForm, form.ModelForm):
    username = form.CharField(label='Логин', required=True)
    email = form.CharField(label='Электронная почта', required=True)
    first_name = form.CharField(label='Имя', required=True)
    last_name = form.CharField(label='Фамилия', required=True)
    password = form.CharField(label='Пароль', widget=form.PasswordInput, required=True)
    confirm_password = form.CharField(label='Подтвердите пароль',
        widget=form.PasswordInput, required=True)

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password', 'confirm_password']

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise form.ValidationError('Пароли несовпадают!')
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
