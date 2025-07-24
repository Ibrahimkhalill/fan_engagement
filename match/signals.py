from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match
from voting.models import Voting, Fan
from django.db.models import Count
from django.db import models
from django.db import transaction
import logging

# Setup logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Match)
def update_voting_points(sender, instance, created, raw, **kwargs):
    # Skip if raw (e.g., fixtures), not finished, or no winner
    if raw or instance.status != 'finished' or not instance.winner:
        return

    try:
        with transaction.atomic():
            # Count votes for team_a, team_b, and draw
            votes = Voting.objects.filter(match=instance).aggregate(
                team_a_votes=Count('pk', filter=models.Q(who_will_win='team_a')),
                team_b_votes=Count('pk', filter=models.Q(who_will_win='team_b')),
                draw_votes=Count('pk', filter=models.Q(who_will_win='draw'))
            )

            # Determine minority vote (fewest votes)
            vote_counts = {
                'team_a': votes['team_a_votes'],
                'team_b': votes['team_b_votes'],
                'draw': votes['draw_votes']
            }
            minority_team = min(vote_counts, key=vote_counts.get)

            # Update points for each vote
            for vote in Voting.objects.filter(match=instance):
                points = 0
                if vote.who_will_win == instance.winner:
                    points += 1  # 1 point for correct winner
                    if vote.who_will_win == minority_team:
                        points += 1  # 1 additional point for minority vote
                    if (vote.goal_difference is not None and 
                        instance.goal_difference is not None and 
                        vote.goal_difference == instance.goal_difference):
                        points += 1  # 1 additional point for correct goal difference
                
                vote.points_earned = points
                vote.save(update_fields=['points_earned'])

                # Update Fan points
                fan, created = Fan.objects.get_or_create(user=vote.user)
                fan.points += points
                fan.save(update_fields=['points'])

            logger.info(f"Points updated for match {instance.id} ({instance.team_a} vs {instance.team_b}) - Winner: {instance.winner}, Minority: {minority_team}, Votes: {votes}")
    except Exception as e:
        logger.error(f"Error updating points for match {instance.id}: {str(e)}")
        raise  # Re-raise to ensure transaction rolls back