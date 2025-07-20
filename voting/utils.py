# your_app_name/utils.py
from django.db.models import Count
from match.models import Match
from .models import Voting
from django.db import models

def get_vote_stats(match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        return {"error": "Match not found"}

    votes = Voting.objects.filter(match=match).aggregate(
        team_a_votes=Count('pk', filter=models.Q(who_will_win='team_a')),
        team_b_votes=Count('pk', filter=models.Q(who_will_win='team_b')),
        draw_votes=Count('pk', filter=models.Q(who_will_win='draw'))
    )

    total_votes = votes['team_a_votes'] + votes['team_b_votes'] + votes['draw_votes']

    if total_votes > 0:
        team_a_percent = (votes['team_a_votes'] / total_votes) * 100
        team_b_percent = (votes['team_b_votes'] / total_votes) * 100
        draw_percent = (votes['draw_votes'] / total_votes) * 100
    else:
        team_a_percent = 0.0
        team_b_percent = 0.0
        draw_percent = 0.0

    return {
        "match_id": match_id,
        "total_votes": total_votes,
        "percentages": {
            "team_a": round(team_a_percent, 1),
            "team_b": round(team_b_percent, 1),
            "draw": round(draw_percent, 1)
        }
    }