from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from .models import News, Service


class NewsOverrideAdminForm(forms.ModelForm):
    body = forms.CharField(
        widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = News
        fields = '__all__'


class ServiceOverrideAdminForm(forms.ModelForm):
    body = forms.CharField(
        widget=CKEditorUploadingWidget(config_name='default')
    )

    class Meta:
        model = Service
        fields = '__all__'