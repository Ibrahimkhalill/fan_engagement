from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match
from voting.models import Voting,Fan
from django.db.models import Count
from django.db import models
from django.db import transaction
import logging

# Setup logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Match)
def update_voting_points(sender, instance, created, raw, **kwargs):
    # Skip if raw (e.g., fixtures) or not finished
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

            # Determine majority vote
            vote_counts = {
                'team_a': votes['team_a_votes'],
                'team_b': votes['team_b_votes'],
                'draw': votes['draw_votes']
            }
            majority_team = max(vote_counts, key=vote_counts.get)

            # Update points for each vote
            for vote in Voting.objects.filter(match=instance):
                points = 0
                if vote.who_will_win == instance.winner:
                    points = 1 if vote.who_will_win == majority_team else 1
                vote.points_earned = points
                vote.save()

                # Update Fan points
                fan, created = Fan.objects.get_or_create(user=vote.user)
                fan.points += points
                fan.save()

            logger.info(f"Points updated for match {instance.id} ({instance.team_a} vs {instance.team_b})")
    except Exception as e:
        logger.error(f"Error updating points for match {instance.id}: {str(e)}")
        raise  # Re-raise to ensure transaction rolls back