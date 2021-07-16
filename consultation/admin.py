from django.contrib import admin
from django.core.mail.message import EmailMessage
from .models import Diagnostic, FeedBack
from .forms import FeedbackForm
from application import settings
from django.views.generic import FormView
from django.utils.html import format_html
from django.core.mail import get_connection, send_mail


@admin.register(Diagnostic)
class FeedbackViewAdmin(admin.ModelAdmin):
    form = FeedbackForm
    fields = ('get_client', 'comment_safe', 'title', 'body')
    readonly_fields = ('comment_safe', 'get_client')
    list_display = ('first_name', 'last_name', 'tool', 'comment')
    list_display_links = ('first_name', 'last_name')

    def get_client(self, obj):
        client = Diagnostic.objects.get(id=obj.id) 
        html = '''
            <p>Отправитель: {0} {1}</p>
            <p>Электронная почта: {2}</p>
            <p>Телефон: {3}</p>
            <p>Инструмент: {4}</p>
        '''
        return format_html(html, client.first_name, client.last_name, client.email, client.phone, client.tool)
    get_client.short_description = 'Информация'
    get_client.allow_tags = True

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=settings.EMAIL_USE_SSL
            )
            message = EmailMessage(
                subject=title,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                bcc=[obj.email]
            )
            message.content_subtype = "html"
            message.send()
        return super().save_model(request, obj, form, change)


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

        
