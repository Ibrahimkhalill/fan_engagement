# your_app_name/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/vote/(?P<match_id>\d+)/$', consumers.VoteConsumer.as_asgi()),
]