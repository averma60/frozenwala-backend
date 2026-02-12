from rest_framework import serializers
from .models import Cart, Whishlist
from django.conf import settings
from menu_management.serializers import ItemSerializer
from .utils import item_stock_quantity

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        base_url = getattr(settings, 'ASSET_URL', '')
        if instance.product_id.item_photo:
            path = str(instance.product_id.item_photo)
            clean_path = path.replace('/media', '') 
            full_url = f"{base_url}{clean_path}"
        else:
            full_url = None

        # Product fields
        old_price = instance.product_id.item_old_price or 0
        new_price = instance.product_id.item_new_price or 0

        # Calculate discount %
        if old_price > 0 and old_price > new_price:
            discount_percentage = round(((old_price - new_price) / old_price) * 100)
        else:
            discount_percentage = 0

        representation['product_id'] = instance.product_id.id
        representation['item_photo'] = full_url
        representation['product_image'] = full_url
        representation['item_new_price'] = "{:.2f}".format(instance.product_id.item_new_price)
        representation['item_old_price'] = "{:.2f}".format(instance.product_id.item_old_price)
        representation['discount_percentage'] = discount_percentage
        representation['totalPrice'] = "{:.2f}".format(instance.price)
        representation['title'] = instance.product_id.title
        representation['product_name'] = instance.product_id.title
        representation['stock'] = item_stock_quantity(instance.product_id.id)
        return representation

class CartGetSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.title', read_only=True)
    price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    def get_price(self, obj):
        return "{:.2f}".format(obj.price)
    
    def get_product_image(self, obj):
        base_url = getattr(settings, 'ASSET_URL', '')
        if obj.product_id.item_photo:
            path = str(obj.product_id.item_photo)
            if path.startswith('/media'):
                path = path[len('/media'):]
            return f"{base_url}{path}"
        return None

    class Meta:
        model = Cart
        fields = ['id', 'product_id', 'u_id', 'quantity', 'price', 'product_name', 'product_image']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        base_url = getattr(settings, 'ASSET_URL', '')

        if instance.product_id.item_photo:
            path = str(instance.product_id.item_photo)
            if path.startswith('/media'):
                path = path[len('/media'):]
            full_url = f"{base_url}{path}"
        else:
            full_url = None

        representation['product_image'] = full_url
        representation['item_old_price'] = "{:.2f}".format(instance.product_id.item_old_price)
        return representation

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whishlist
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['item'] = ItemSerializer(instance.item).data
        return representation
