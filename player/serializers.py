from rest_framework import serializers
from .models import Player

class RelativeImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        # শুধু /media/... path return করবে
        return f"/media/{value.name}"


class PlayerSerializer(serializers.ModelSerializer):
    image = RelativeImageField()
    class Meta:
        model = Player
        fields = ['id', 'image', 'name', 'jersey_number','status']



