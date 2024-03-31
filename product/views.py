from django.shortcuts import render
from rest_framework import viewsets

from product.models import PlanetariumDome
from product.serializers import PlanetariumDomeSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
