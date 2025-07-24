from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/vote/(?P<match_id>\d+)/$', consumers.VoteConsumer.as_asgi()),
    re_path(r'^ws/match_status/$', consumers.MatchStatusConsumer.as_asgi()),
]
