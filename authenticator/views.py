import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from store.models import Customer
from store.utils import BaseListView

from .forms import LoginForm, SigninForm


class LoginView(BaseListView, LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def get_success_url(self) -> str:
        return self.success_url

    def form_valid(self, form):
        if not self.request.recaptcha_is_valid:
            return self.form_invalid(form)
        return super().form_valid(form)


class SigninView(BaseListView, CreateView):
    template_name = 'login.html'
    form_class = SigninForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if self.request.recaptcha_is_valid:
            form_valid = super().form_valid(form)
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            auth_user = authenticate(username=username, first_name=first_name, last_name=last_name,
                                    password=password, email=email)
            customer = Customer(user=auth_user)
            customer.save()
            login(self.request, auth_user)
            return form_valid
        return self.form_invalid(form)


class LogoutView(LogoutView):
    next_page = reverse_lazy('home')


class CustomChangePasswordView(BaseListView, View):
    template_name = 'custom-auth-action.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = PasswordChangeForm(request.user)
            context = {
                'change_password_form': form,
                'cart_info': self.cart_info
            }
            return render(request, self.template_name, context=context)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid() and request.recaptcha_is_valid:
            user = form.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.INFO,
                                 'Вы успешно поменяли пароль!')
        else:
            messages.add_message(request, messages.INFO,
                                 'Пожалуйста, введите корректные данные!')
            return HttpResponseRedirect(reverse('change-password-custom-view'))
        return HttpResponseRedirect(reverse('profile'))
