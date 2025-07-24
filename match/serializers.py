# from rest_framework import serializers
# from .models import  Match
# from django.contrib.auth.models import User
# from player.models import Player
# from player.serializers import PlayerSerializer


# class FlexiblePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
#     def to_internal_value(self, data):
#         try:
#             data = int(data)  # convert "1" → 1
#         except (ValueError, TypeError):
#             self.fail('incorrect_type', data_type=type(data).__name__)
#         return super().to_internal_value(data)

# class MatchSerializer(serializers.ModelSerializer):
#     selected_players = PlayerSerializer(many=True, read_only=True)
#     selected_players_ids = FlexiblePrimaryKeyRelatedField(
#         queryset=Player.objects.all(),
#         source='selected_players',
#         many=True,
#         write_only=True,
#         required=False
#     )

#     class Meta:
#         model = Match
#         fields = [
#             'id', 'team_a', 'team_b','team_a_pics','team_b_pics',
#             'time', 'date',
#             'selected_players', 'selected_players_ids',
#             'winner', 'status', 'win_name', "goal_difference"
#         ]
        
        


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

    # Add match_timezone as optional input (default UTC if not provided)
    match_timezone = serializers.CharField(write_only=True, required=False, default='UTC')

    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b','team_a_pics','team_b_pics',
            'time', 'date',
            'selected_players', 'selected_players_ids',
            'winner', 'status', 'win_name', 'goal_difference',
            'match_timezone',
        ]

    def _convert_to_utc(self, date, time, tz_str):
        # Combine date & time to naive datetime
        naive_dt = datetime.combine(date, time)
        # Get pytz timezone
        local_tz = pytz_timezone(tz_str)
        # Localize naive datetime to given timezone
        local_dt = local_tz.localize(naive_dt)
        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz_timezone('UTC'))
        return utc_dt.date(), utc_dt.time()

    def create(self, validated_data):
        tz_str = validated_data.pop('match_timezone', 'UTC')
        date = validated_data.get('date')
        time = validated_data.get('time')
        if date and time:
            utc_date, utc_time = self._convert_to_utc(date, time, tz_str)
            validated_data['date'] = utc_date
            validated_data['time'] = utc_time

        # Save timezone field explicitly
        validated_data['match_timezone'] = tz_str

        return super().create(validated_data)

    def update(self, instance, validated_data):
        tz_str = validated_data.pop('match_timezone', instance.match_timezone if hasattr(instance, 'match_timezone') else 'UTC')
        date = validated_data.get('date', instance.date)
        time = validated_data.get('time', instance.time)
        if date and time:
            utc_date, utc_time = self._convert_to_utc(date, time, tz_str)
            validated_data['date'] = utc_date
            validated_data['time'] = utc_time

        validated_data['match_timezone'] = tz_str

        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # Use the match's own timezone field from instance
        tz_str = getattr(instance, 'match_timezone', 'UTC') or 'UTC'
        print(f"[TO_REPRESENTATION] Using timezone: {tz_str}")
        local_tz = pytz_timezone(tz_str)

        naive_dt = datetime.combine(instance.date, instance.time)
        utc_dt = pytz_timezone('UTC').localize(naive_dt)

        local_dt = utc_dt.astimezone(local_tz)

        ret['date'] = local_dt.date().isoformat()
        ret['time'] = local_dt.time().strftime('%H:%M:%S')
        ret['timezone'] = tz_str

        return ret
