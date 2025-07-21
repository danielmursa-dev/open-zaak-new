import uuid

from django.db import models
# Create your models here.


class Zaak(models.Model):
    omschrijving = models.CharField(
        max_length=80,
        blank=True,
        help_text="Een korte omschrijving van de zaak.",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)",
    )
