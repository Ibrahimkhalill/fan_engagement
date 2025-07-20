from django.db import models
from player.models import Player
from django.contrib.auth import get_user_model
User = get_user_model()

class Match(models.Model):
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    team_a_pics = models.ImageField(
        upload_to='matches/', blank=True, null=True,
    )
    team_b_pics =  models.ImageField(
        upload_to='matches/', blank=True, null=True,
    )
    time = models.TimeField()
    date = models.DateField()
    selected_players = models.ManyToManyField(Player, blank=True)
    winner = models.CharField(
        max_length=20,
        choices=[('team_a', 'Team A'), ('team_b', 'Team B'), ('draw', 'Draw')],
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[('upcoming', 'Upcoming'), ('live', 'Live'), ('finished', 'Finished')],
        default='upcoming',
        blank=True,null=True
    )
    win_name = models.CharField(max_length=100, blank=True, null=True)  # Stores winning team name

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} on {self.date}"

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
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date', 'time']),
            models.Index(fields=['status']),
        ]