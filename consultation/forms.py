from django.forms import fields
from consultation.models import Diagnostic, FeedBack
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms.fields import EmailField
from store.forms import BaseForm


class DiagnosticForm(BaseForm, forms.Form):
    first_name = forms.CharField(
        label='Имя',
        max_length=255
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=255
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=11,
        required=False,
        widget=forms.NumberInput(attrs={'type': 'tel'})
    )
    email = forms.EmailField(
        label='Электронная почта',
        required=False
    )
    tool = forms.CharField(
        label='Инструмент',
        help_text='Производитель, тип, модель, год'
    )
    problem_description = forms.CharField(
        widget=CKEditorUploadingWidget(config_name='contact_ckeditor'),
        label='Опишите проблему'
    )


class FeedbackForm(forms.ModelForm):
    title = forms.CharField(max_length=255, label='Заголовок')
    body = forms.CharField(
        widget=CKEditorUploadingWidget(config_name='default'),
        label='Тело письма'
    )

    class Meta:
        model = FeedBack
        exclude = ('first_name', 'last_name', 'email', 'phone', 'tool', 'comment', 'is_active')