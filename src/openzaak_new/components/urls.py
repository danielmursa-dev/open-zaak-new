from django.urls import include, path

urlpatterns = [
    path("zaken/api/", include("openzaak_new.components.zaken.api.urls")),
    path("catalogi/api/", include("openzaak_new.components.catalogi.api.urls")),
]
