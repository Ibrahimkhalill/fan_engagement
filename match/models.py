from django.db import models
from player.models import Player
from django.contrib.auth import get_user_model
User = get_user_model()


class Match(models.Model):
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    team_a_pics = models.ImageField(
        upload_to='matches/',
        blank=True,
        null=True,
        max_length=1000  # practically almost unlimited
    )
    team_b_pics = models.ImageField(
        upload_to='matches/',
        blank=True,
        null=True,
        max_length=1000
    )
    date_time = models.DateTimeField(blank=True, null=True)
    selected_players = models.ManyToManyField(Player, blank=True)
    winner = models.CharField(
        max_length=20,
        choices=[('team_a', 'Team A'), ('team_b', 'Team B'), ('draw', 'Draw')],
        blank=True,
        null=True
    )
    goal_difference = models.IntegerField(default=0, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('upcoming', 'Upcoming'), ('live', 'Live'),
                 ('finished', 'Finished'), ('inactive', 'Inactive')],
        default='upcoming',
        blank=True, null=True
    )
    # Stores winning team name
    win_name = models.CharField(max_length=100, blank=True, null=True)

    # Add this field to store match timezone as a string, default to UTC
    match_timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text='Timezone of the match (e.g., Asia/Dhaka, America/New_York)'
    )
    points_calculated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} on {self.date_time}"

    def save(self, *args, **kwargs):
        # Auto-set win_name based on winner
        if self.winner == 'team_a':
            self.win_name = self.team_a
        elif self.winner == 'team_b':
            self.win_name = self.team_b
        elif self.winner == 'draw':
            self.win_name = 'Draw'
        else:
            self.win_name = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date_time']
        indexes = [
            models.Index(fields=['date_time']),
            models.Index(fields=['status']),
        ]
