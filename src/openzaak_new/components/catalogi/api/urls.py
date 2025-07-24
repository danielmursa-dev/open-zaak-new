# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from django.urls import include, path, re_path

from vng_api_common import routers

from .viewsets import ZaakTypeViewSet

router = routers.DefaultRouter()
router.register(r"zaaktypen", ZaakTypeViewSet)

urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include(
            [
                # actual API
                path("", include(router.urls)),
                path("", router.APIRootView.as_view(), name="api-root-catalogi"),
                path("", include("vng_api_common.notifications.api.urls")),
            ]
        ),
    )
]
