# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogiConfig(AppConfig):
    name = "openzaak_new.components.catalogi"
    verbose_name = _("Catalogi")

    def ready(self):
        pass
