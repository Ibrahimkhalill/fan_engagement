
from rest_framework import serializers
from .models import Match
from player.models import Player
from player.serializers import PlayerSerializer
from pytz import timezone as pytz_timezone
from datetime import datetime

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
    match_timezone = serializers.CharField(write_only=True, required=False, default='UTC')

    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b', 'team_a_pics', 'team_b_pics',
            'date_time',
            'selected_players', 'selected_players_ids',
            'winner', 'status', 'win_name', 'goal_difference',
            'match_timezone',
        ]

    
