
import threading
import time
from datetime import timedelta
from django.utils import timezone
from match.models import Match
from match.serializers import MatchSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

from pytz import UTC
from datetime import datetime, timedelta
from django.utils import timezone
print(settings.TIME_ZONE)

def match_status_scheduler():
    print("Starting match status scheduler...")
    def update():
        while True:
            now = timezone.localtime()
            print(f"Current time: {now}")
            matches = Match.objects.filter(status__in=["upcoming", "live"])
            if not matches:
                print("No matches to check status.")
                time.sleep(30)
           
            for match in matches:
                print(f"Checking match {match.id} status...")
                print(f"Match date: {match.date}, time: {match.time}")
                match_time = datetime.combine(match.date, match.time)  # naive UTC
                match_time = UTC.localize(match_time)  # aware UTC
                
                changed = False

                # If match is upcoming and it's time to start → set to live
                if match.status == "upcoming" and match_time <= now < match_time + timedelta(hours=2):
                    match.status = "live"
                    changed = True

                # If match is live and 2 hours passed → set to finished
                elif match.status == "live" and now >= match_time + timedelta(hours=2):
                    match.status = "finished"
                    changed = True

                if changed:
                    match.save()

                    # Serialize match
                    serializer = MatchSerializer(match)

                    # Send update to dynamic group for this match
                    group_name = "match_status_all"
                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "match_status_update",
                            "match_id": match.id,
                            # you can also send minimal data if you want
                        }
                    )
            print("Match status updated.")

            time.sleep(30)  # Check every 30 seconds

    # Run in background thread
    thread = threading.Thread(target=update, daemon=True)
    thread.start()