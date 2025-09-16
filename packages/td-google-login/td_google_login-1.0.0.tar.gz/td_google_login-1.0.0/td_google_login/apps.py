from django.apps import AppConfig


class TdGoogleLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'td_google_login'
    verbose_name = 'TD Google Login'
    
    def ready(self):
        """
        Import signals when the app is ready.
        """
        try:
            import td_google_login.signals
        except ImportError:
            pass
