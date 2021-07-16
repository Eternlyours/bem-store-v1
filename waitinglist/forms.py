from django import forms
from .models import WaitingList
from store.forms import BaseForm


class WaitingListForm(BaseForm, forms.Form):
    email = forms.EmailField(label='Электронная почта')