from rest_framework import serializers
from .models import  Match
from django.contrib.auth.models import User
from player.models import Player
from player.serializers import PlayerSerializer


class FlexiblePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            data = int(data)  # convert "1" → 1
        except (ValueError, TypeError):
            self.fail('incorrect_type', data_type=type(data).__name__)
        return super().to_internal_value(data)

class MatchSerializer(serializers.ModelSerializer):
    selected_players = PlayerSerializer(many=True, read_only=True)
    selected_players_ids = FlexiblePrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        source='selected_players',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b','team_a_pics','team_b_pics',
            'time', 'date',
            'selected_players', 'selected_players_ids',
            'winner', 'status', 'win_name'
        ]