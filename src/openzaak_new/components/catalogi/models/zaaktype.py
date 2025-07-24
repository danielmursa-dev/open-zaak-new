# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class ZaakType(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    identificatie = models.CharField(
        _("identificatie"),
        max_length=50,
        blank=True,
        help_text=_(
            "Unieke identificatie van het ZAAKTYPE binnen de CATALOGUS waarin het ZAAKTYPE voorkomt."
        ),
        db_index=True,
    )

    class Meta:
        verbose_name = _("Zaaktype")
        verbose_name_plural = _("Zaaktypen")
