from django.urls import path
from . import views

urlpatterns = [
    path('votings/list/', views.voting_list_create, name='voting-list-create'),
    path('votings/<int:pk>/', views.voting_detail, name='voting-detail'),
    path('votes/', views.vote_create, name='vote-create'),
    
    path('votes/check-user/<int:match_id>/', views.check_user_vote),
    
    path('vote-stats/<int:match_id>/', views.vote_stats, name='vote-stats'), 
    path('engagement-stats-totals/', views.engagement_stats, name='match-voting-totals'),
      # New endpoint
    path('fans/me/', views.fan_points, name='fan-points'),
    path('fans/leaderboard/', views.fan_leaderboard, name='fan-leaderboard'),
    
    
    path('player-selection-stats/<int:match_id>/', views.player_selection_stats, name='player-selection-stats'),
]

