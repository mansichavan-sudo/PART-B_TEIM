# crmapp/apps.py
from django.apps import AppConfig


class CrmappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crmapp'

    def ready(self):
        """
        Import signals when the app is ready.
        Wrapped in try-except to avoid import issues during migrations or reload.
        """
        try:
            import crmapp.signals
        except ImportError as e:
            import logging
            logging.warning(f"⚠️ Could not import signals: {e}")

