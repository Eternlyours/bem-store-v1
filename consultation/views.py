from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.views import View

from .forms import DiagnosticForm
from .models import Diagnostic


class ConsultationView(View):

    def post(self, request, *args, **kwargs):
        form = DiagnosticForm(request.POST)
        if form.is_valid():
            Diagnostic.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                tool=form.cleaned_data['tool'],
                comment=form.cleaned_data['problem_description']
            )
            messages.add_message(request, messages.INFO,
            'Заявка отправлена! Ожидайте.')
        return HttpResponseRedirect('/')
