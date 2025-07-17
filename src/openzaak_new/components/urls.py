from django.urls import include, path

urlpatterns = [
    path("zaken/api/", include("openzaak_new.components.zaken.api.urls")),
]
