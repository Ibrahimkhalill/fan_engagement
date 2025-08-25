
from rest_framework import serializers
from .models import Match
from player.models import Player
from player.serializers import PlayerSerializer
from pytz import timezone as pytz_timezone
from datetime import datetime
from voting.models import Voting
from django.db import models

class RelativeImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        # শুধু /media/... path return করবে
        return f"/media/{value.name}"
class FlexiblePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            data = int(data)  # convert "1" → 1
        except (ValueError, TypeError):
            self.fail('incorrect_type', data_type=type(data).__name__)
        return super().to_internal_value(data)

class MatchCreateSerializer(serializers.ModelSerializer):
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
    top_players = serializers.SerializerMethodField()  # 👈 নতুন ফিল্ড
    team_a_pics = RelativeImageField()
    team_b_pics = RelativeImageField()
    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b', 'team_a_pics', 'team_b_pics',
            'date_time',
            'selected_players', 'selected_players_ids',
            'winner', 'status', 'win_name', 'goal_difference',
            'match_timezone',
            'top_players',   # 👈 add করলাম
        ]



    def get_top_players(self, obj):
        # সব vote এই ম্যাচের
        votes = Voting.objects.filter(match=obj).prefetch_related("selected_players")

        # player নির্বাচন count রাখব
        from collections import Counter
        player_count = Counter()

        for vote in votes:
            for player in vote.selected_players.all():
                player_count[player.id] += 1

        total_selections = sum(player_count.values())

        if total_selections == 0:
            return []

        # top 3 player বের করা
        top_three = player_count.most_common(3)

        # Player details + percentage বানানো
        results = []
        for player_id, count in top_three:
            try:
                player = Player.objects.get(id=player_id)
                percentage = round((count / total_selections) * 100, 2)
                results.append({
                    "id": player.id,
                    "name": player.name,
                    "selections": count,
                    "percentage": percentage
                })
            except Player.DoesNotExist:
                continue

        return results
