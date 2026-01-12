from rest_framework import serializers
from .models import WalletBenefit, PurchaseBenefit

class WalletBenefitSerializer(serializers.ModelSerializer):
    influencer_valid_days = serializers.SerializerMethodField()

    class Meta:
        model = WalletBenefit
        fields = [
            'id',
            'add_amount',
            'benefit_amount',
            'description',
            'influencer',
            'influencer_valid_days',
            'is_active',
        ]

    def get_influencer_valid_days(self, obj):
        return obj.influencer_time_period.days if obj.influencer_time_period else None

class PurchaseBenefitSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseBenefit
        fields = [
            'id',
            'price',
            'benefit_percentage'
        ]
