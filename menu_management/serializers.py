

from rest_framework import serializers
from .models import Item, ItemReview
from ecomApp.models  import Catagory,Stock, DeliveryCharge
from django.conf import settings
from ecomApp.models import Catagory

class ItemSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    item_photo = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'

    def get_stock(self, obj):        
        stock = Stock.objects.filter(item_id=obj).first()
        return stock.openingstock if stock else None
    
    def get_item_photo(self, obj):
        base_url = getattr(settings, 'ASSET_URL', '')
        if obj.item_photo:
            clean_path = str(obj.item_photo).replace('/media', '')
            return f"{base_url}{clean_path}"
        return ""
    
    def get_discount_percentage(self, obj):
        old_price = getattr(obj, "item_old_price", 0)
        new_price = getattr(obj, "item_new_price", 0)
        if old_price and new_price and old_price > new_price:
            return round(((old_price - new_price) / old_price) * 100)
        return 0

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Catagory
        fields = '__all__'

class ItemReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = ItemReview
        fields = [
            'id',
            'user_name',
            'rating',
            'review_text',
            'created_at'
        ]
