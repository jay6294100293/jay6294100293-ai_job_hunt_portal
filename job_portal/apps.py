from django.apps import AppConfig


class JobPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_portal'

    def ready(self):
        try:
            import ai_job_hunt.signals  # Import signal handlers
        except ImportError:
            pass
