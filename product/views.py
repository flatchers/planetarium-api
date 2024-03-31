from django.shortcuts import render
from rest_framework import viewsets

from product.models import PlanetariumDome, ShowTheme
from product.serializers import PlanetariumDomeSerializer, ShowThemeSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

