from rest_framework import serializers
from .models import  Advertisement

class RelativeImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        # শুধু /media/... path return করবে
        return f"/media/{value.name}"

class AdvertisementSerializer(serializers.ModelSerializer):
    image = RelativeImageField()
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'url', 'image', 'created_at']