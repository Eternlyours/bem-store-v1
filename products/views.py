from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Product, ProductUserAction


@login_required(login_url='login')
def add_to_favorite_list(request, slug):
    product = get_object_or_404(Product, slug=slug)
    favorite_list, created = ProductUserAction.objects.get_or_create(
        product=product, user=request.user)
    if created:
        favorite_list.favorite = True
        messages.add_message(request, messages.INFO,
                             'Товар добавлен в список понравившихся')
    elif not created and not favorite_list.favorite:
        favorite_list.favorite = True
        messages.add_message(request, messages.INFO,
                             'Товар добавлен в список понравившихся')
    else:
        favorite_list.favorite = False
        messages.add_message(request, messages.INFO,
                             'Товар удалён из списка понравившихся')
    favorite_list.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
