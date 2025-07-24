from django.apps import AppConfig

class VotingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voting'

    def ready(self):
        # Import here to avoid app registry errors
        from .schuduler import match_status_scheduler
        match_status_scheduler()
