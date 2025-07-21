from django.urls import include, path, re_path

from vng_api_common import routers

from .viewsets import ZaakViewSet

router = routers.DefaultRouter()
router.register("zaken", ZaakViewSet)


urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include([path("", include(router.urls))]),
    )
]
