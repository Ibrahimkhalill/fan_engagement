from rest_framework import serializers
from .models import  Voting ,Fan
from player.models import Player
from django.contrib.auth import get_user_model
User = get_user_model()
from player.serializers import PlayerSerializer
from match.models import Match
from authentications.serializers import CustomUserSerializer

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'team_a', 'team_b', 'date', 'time', 'status', 'selected_players']
        read_only_fields = ['id', 'status', 'selected_players']

class VotingSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())
    selected_players = PlayerSerializer(many=True, read_only=True)
    selected_players_ids = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(), source='selected_players', many=True, write_only=True, required=False
    )
    

    class Meta:
        model = Voting
        fields = ['id', 'user', 'match', 'who_will_win', 'goal_difference', 'selected_players', 'selected_players_ids', 'points_earned']
        read_only_fields = ['id', 'user', 'points_earned']

    def validate(self, data):
        match = data['match']
        if match.status == 'finished':
            raise serializers.ValidationError({"match": "Cannot vote on a finished match."})
        
        selected_players = data.get('selected_players', [])
        if len(selected_players) > 3:
            raise serializers.ValidationError({"selected_players": "Cannot select more than 3 players."})
        for player in selected_players:
            if player not in match.selected_players.all():
                raise serializers.ValidationError({"selected_players": f"Player {player.name} is not in this match."})
        
       
        
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        match = instance.match
        if instance.who_will_win == 'team_a':
            representation['who_will_win'] = match.team_a
        elif instance.who_will_win == 'team_b':
            representation['who_will_win'] = match.team_b
        else:
            representation['who_will_win'] = 'Draw'
        return representation

    def to_internal_value(self, data):
        data = data.copy()
        match_id = data.get('match')
        if not match_id:
            raise serializers.ValidationError({"match": "This field is required."})
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise serializers.ValidationError({"match": "Invalid match ID."})
        
        who_will_win = data.get('who_will_win')
        if who_will_win == match.team_a:
            data['who_will_win'] = 'team_a'
        elif who_will_win == match.team_b:
            data['who_will_win'] = 'team_b'
        elif who_will_win == 'Draw':
            data['who_will_win'] = 'draw'
        
        
        return super().to_internal_value(data)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class FanSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Fan
        fields = ['user', 'points', 'rank']

    def get_rank(self, obj):
        # Get rank from context (integer)
        rank = self.context.get('ranks', {}).get(self.instance.index(obj) if self.instance else 0, 1)
        
        return rank