from django.apps import AppConfig


class ZakenConfig(AppConfig):
    name = "openzaak_new.components.zaken"

    def ready(self):
        pass
        # from .api.viewsets import ZaakViewSet
