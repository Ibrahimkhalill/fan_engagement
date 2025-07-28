from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match
from voting.models import Voting, Fan
from django.db.models import Count
from django.db import models
from django.db import transaction
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Setup logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Match)
def update_voting_points(sender, instance, created, raw, **kwargs):
    # Skip if raw (e.g., fixtures), not finished, no winner, or instance is deleted
    if raw or instance.status != 'finished' or not instance.winner:
        return
    
      # ❗ Skip if already calculated
    if instance.points_calculated:
        logger.info(f"Points already calculated for match {instance.id}, skipping.")
        return

    # Check if the Match instance still exists in the database
    try:
        Match.objects.get(pk=instance.pk)
    except Match.DoesNotExist:
        logger.debug(f"Match {instance.id} was deleted, skipping points update")
        return

    try:
        with transaction.atomic():
            # Count votes for team_a, team_b, and draw
            votes = Voting.objects.filter(match=instance).aggregate(
                team_a_votes=Count('pk', filter=models.Q(who_will_win='team_a')),
                team_b_votes=Count('pk', filter=models.Q(who_will_win='team_b')),
                draw_votes=Count('pk', filter=models.Q(who_will_win='draw'))
            )

            # Determine majority vote (most votes)
            vote_counts = {
                'team_a': votes['team_a_votes'],
                'team_b': votes['team_b_votes'],
                'draw': votes['draw_votes']
            }
            majority_team = max(vote_counts, key=vote_counts.get)
            
            print(f"Votes for match {instance.id}: {vote_counts}, Majority: {majority_team}")

            # Update points for each unique vote (skip duplicate user votes)
            seen_users = set()
            all_votes = Voting.objects.filter(match=instance).select_related('user')

            for vote in all_votes:
                if vote.user_id in seen_users:
                    logger.warning(f"Duplicate vote detected for user {vote.user_id} in match {instance.id}, skipping.")
                    continue
                seen_users.add(vote.user_id)

                points = 0
                if vote.who_will_win == instance.winner:
                    points += 1  # 1 point for correct winner
                    if instance.winner != majority_team:
                        points += 1  # 1 additional point if winner is not the majority vote
                    if (vote.goal_difference is not None and 
                        instance.goal_difference is not None and 
                        vote.goal_difference == instance.goal_difference):
                        points += 1  # 1 additional point for correct goal difference

                vote.points_earned = points
                vote.save(update_fields=['points_earned'])

                # Update Fan points
                fan, _ = Fan.objects.get_or_create(user=vote.user)
                fan.points += points
                fan.save(update_fields=['points'])
                
            instance.points_calculated = True
            instance.save(update_fields=["points_calculated"])

            # WebSocket notify all clients
            group_name = "match_status_all"
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "match_status_update",
                    "match_id": instance.id,
                }
            )

            logger.info(f"Points updated for match {instance.id} ({instance.team_a} vs {instance.team_b}) - Winner: {instance.winner}, Majority: {majority_team}, Votes: {vote_counts}")
    except Exception as e:
        logger.error(f"Error updating points for match {instance.id}: {str(e)}")
        raise  # Re-raise to ensure transaction rolls back
