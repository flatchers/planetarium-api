from django.urls import path, include
from rest_framework import routers

from product.views import PlanetariumDomeViewSet

router = routers.DefaultRouter()
router.register("planetarium_domes", PlanetariumDomeViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "planetarium"
