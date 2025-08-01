from django.apps import AppConfig


class ProfilesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles_app'

    def ready(self):
        import profiles_app.signals  # Import signals here to connect them on app startup