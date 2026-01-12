from rest_framework import serializers
from .models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    add_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Advertisement
        fields = '__all__'
    
    def get_add_photo(self, obj):
        request = self.context.get("request")
        if obj.add_photo and request:
            return request.build_absolute_uri(obj.add_photo.url)
        return None