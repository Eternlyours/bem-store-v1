from ckeditor.widgets import CKEditorWidget
from django import forms
from store.models import Brand, Category



def get_tuple_category():
    choices = ()
    try:
        choices = tuple(Category.objects.all().values_list('slug', 'name'))
    except:
        pass
    return choices


def get_tuple_brand():
    choices = ()
    try:
        choices = tuple(Brand.objects.all().values_list('name', 'name'))
    except:
        pass
    return choices


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            # if visible.field.label == 'Категория':
            #     visible.field.widget.attrs['class'] = 'list-unstyled'


class SearchForm(BaseForm, forms.Form):
    q = forms.CharField(label=False)


class CommentForm(BaseForm, forms.Form):
    body = forms.CharField(widget=CKEditorWidget(
        config_name='comment_ckeditor'), required=True, label=False)