import uuid

from django.db import models

# Create your models here.
from vng_api_common.models import APIMixin as _APIMixin


class APIMixin(_APIMixin):
    def get_absolute_api_url(self, request=None, **kwargs) -> str:
        kwargs["version"] = "1"
        return super().get_absolute_api_url(request=request, **kwargs)


class Zaak(APIMixin, models.Model):
    omschrijving = models.CharField(
        max_length=80,
        blank=True,
        help_text="Een korte omschrijving van de zaak.",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)",
    )
