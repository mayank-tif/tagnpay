from django.apps import AppConfig


class TagnpayloyaltyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tagnpayloyalty'

    def ready(self):
        import signals.globaldata_signals  # Ensure signals are imported