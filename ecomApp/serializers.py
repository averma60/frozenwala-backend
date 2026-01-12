# serializers.py
from rest_framework import serializers
from .models import Stock
from .models import CustomerCoupon
from datetime import datetime, timedelta

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class CustomerCouponSerializer(serializers.ModelSerializer):
    time_remaining = serializers.SerializerMethodField()

    def get_time_remaining(self, obj):
        today = datetime.now().date()
        if today < obj.start_date:
            remaining = obj.start_date - today
            return f"{remaining.days} days until start"
        elif today > obj.expire_date:
            return "Coupon has expired"
        else:
            remaining = obj.expire_date - today
            return f"{remaining.days} days remaining"

    class Meta:
        model = CustomerCoupon
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Assuming instance.item_photo is the image path
        representation['image'] = instance.image.url if instance.image else None
        return representation
