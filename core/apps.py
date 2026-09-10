from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Monitoring System Core"

    def ready(self):
        """Run startup tasks when Django is ready."""
        from core.utils.helpers import setup_defaults
        try:
            setup_defaults()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("setup_defaults failed: %s", e)
