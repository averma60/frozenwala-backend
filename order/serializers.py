from rest_framework import serializers
from .models import Order, PaymentOption
from menu_management.models import Item

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class GroupedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'total_price', 'status')

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'item_photo', 'item_quantity', 'item_measurement',
                  'item_old_price', 'discount', 'item_new_price', 'status', 'category', 'created_at',
                  'deal_of_the_day', 'recommended', 'most_popular']

class PaymentOptionSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_code_display', read_only=True)

    class Meta:
        model = PaymentOption
        fields = [
            'id',
            'code',
            'display_name',
            'is_active',
            'description'
        ]