from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        from . import models
        try:
            if not models.Modulo.objects.all():
                from . import views
                print(views.crear_super_usuario('Holo'))
        except Exception as e:
            print(e)