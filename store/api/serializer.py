from rest_framework import serializers
from products.models import Photo, Product
from store.models import Brand, Category


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()
    images = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'model', 'article', 'brand',
                  'category', 'price', 'description', 'images')
