import threading
import time
from datetime import timedelta
from django.utils import timezone
from match.models import Match
from match.serializers import MatchSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def match_status_scheduler():
    print("Starting match status scheduler...")

    def update():
        while True:
            now = timezone.now()  # UTC-aware
            print(f"Current UTC time: {now}")

            matches = Match.objects.filter(status__in=["upcoming", "live"])
            if not matches:
                print("No matches to check status.")
                time.sleep(30)
                continue

            for match in matches:
                print(f"Checking match {match.id} status...")
                print(f"Match datetime (UTC in DB): {match.date_time}")

                changed = False

                # upcoming → live
                if match.status == "upcoming" and match.date_time <= now < match.date_time + timedelta(hours=2):
                    match.status = "live"
                    changed = True

                # live → finished
                elif match.status == "live" and now >= match.date_time + timedelta(hours=2):
                    match.status = "finished"
                    changed = True

                if changed:
                    match.save()

                    # Send update to WebSocket group
                    group_name = "match_status_all"
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "match_status_update",
                            "match_id": match.id,
                        }
                    )
                    print(f"Match {match.id} status changed to {match.status}")

            print("Match status check cycle completed.")
            time.sleep(30)

    thread = threading.Thread(target=update, daemon=True)
    thread.start()
