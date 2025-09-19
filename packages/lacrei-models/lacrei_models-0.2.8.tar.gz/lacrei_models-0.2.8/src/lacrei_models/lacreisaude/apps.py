from django.apps import AppConfig
import watson


class LacreiSaudeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lacrei_models.lacreisaude"

    def ready(self):
        from lacrei_models.lacreisaude.models import Professional
        watson.register(Professional)