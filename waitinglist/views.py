from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from products.models import Product

from .models import WaitingList


class WaitingListView(View):

    def get(self, request):
        email = request.GET.get('email')
        slug = request.GET.get('product')
        product = get_object_or_404(Product, slug=slug)
        waitinglist = get_object_or_404(WaitingList, email=email, product=product)
        waitinglist.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


