from django.urls import path, include
from rest_framework import routers

from product.views import PlanetariumDomeViewSet, ShowThemeViewSet, AstronomyShowViewSet

router = routers.DefaultRouter()
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("show_themes", ShowThemeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "planetarium"
