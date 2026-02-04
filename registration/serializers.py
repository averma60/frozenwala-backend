# serializers.py
from rest_framework import serializers
from ecomApp.models import CustomUser
from influencer.models import InfluencerRecord
from django.utils.timezone import now
from order.models import Order
# class RegistrationSerializer(serializers.Serializer):
#     phone_number = serializers.CharField()
#     otp = serializers.CharField()
class CustomUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('phone_number',  'otp_value', 'name', 'influencer_code', 'refer_by')

    def create(self, validated_data):
        # Set the walet attribute to 0.0 in the validated_data dictionary
        # validated_data['walet'] = 11.0

        # Create the user with the updated validated_data
        user = CustomUser.objects.create_user(**validated_data)
        return user

class InfluencerRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfluencerRecord
        fields = ['start_date', 'end_date', 'benefit_percentage']

class ProfileSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()
    influencer_record = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'required': False},
            'phone_number': {'required': False},
            'email': {'required': False},
        }

    def get_referral_link(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/ref/frzn/?referral_code={obj.referral_code}')
        return None

    def get_influencer_record(self, obj):
        influencer_record = InfluencerRecord.objects.filter(user=obj, end_date__gte=now()).first()
        return InfluencerRecordSerializer(influencer_record).data if influencer_record else None

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'bio','profile_photo']
        extra_kwargs = {
            'password': {'required': False},  # Allow password to be optional
            'email': {'required': False},  # Make email optional
            'bio': {'required': False},
            'name': {'required': False},
            # Make bio optional
            'profile_photo': {'required': False},
        }

from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
# address/serializers.py
from rest_framework import serializers
from .models import AddressAdmin

class AddressAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressAdmin
        fields = '__all__'

class MyRefferalsSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField()
    total_order_amount = serializers.SerializerMethodField()
    last_purchased_at = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['name', 'phone_number', 'profile_photo', 'order_count', 'total_order_amount', 'last_purchased_at']

    def get_order_count(self, obj):
        total_orders = Order.objects.filter(user_id=obj.id)
        return total_orders.count()

    def get_total_order_amount(self, obj):
        total_orders = Order.objects.filter(user_id=obj.id)
        total_price = 0
        for item in total_orders:
            total_price += item.product_id.item_old_price * item.quantity
        
        first_order = total_orders.first()
        if first_order and first_order.delivery_price:
            total_price += int(first_order.delivery_price)

        return total_price

    def get_last_purchased_at(self, obj):
        last_order = Order.objects.filter(user_id=obj.id).order_by('-created_at').first()
        return last_order.created_at if last_order else None
