from match.models import Match
from player.models import Player
from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class Voting(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, blank=True, null=True)  # Link to Match
    who_will_win = models.CharField(max_length=100, choices=[('team_a', 'Team A'), (
        'team_b', 'Team B'), ('draw', 'Draw')], blank=True, null=True)  # Team A or B
    goal_difference = models.IntegerField(
        null=True, blank=True)  # null if no diff specified
    selected_players = models.ManyToManyField(Player, blank=True)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure selected_players are from the match
        if self.selected_players.count() > 3:
            raise ValidationError("Cannot select more than 3 players.")
        for player in self.selected_players.all():
            if player not in self.match.selected_players.all():
                raise ValidationError(
                    f"Player {player.name} is not in this match.")

    class Meta:
        unique_together = ('user', 'match')


class Fan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} ({self.points} points)"
