from rest_framework import permissions
from rest_framework.generics import ListAPIView
from products.models import Photo, Product
from store.models import Category, Brand

from .serializer import (BrandSerializer, CategorySerializer, PhotoSerializer,
                         ProductSerializer)


class ProductListAPI(ListAPIView):
    queryset = Product.objects.select_related(
        'brand').select_related('category').all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = ProductSerializer


class CategoryListAPI(ListAPIView):
    queryset = Category.objects.prefetch_related('parent').all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = CategorySerializer


class BrandListAPI(ListAPIView):
    queryset = Brand.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BrandSerializer
