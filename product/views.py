from django.db.models import Count, F
from django.shortcuts import render
from rest_framework import viewsets, pagination

from product.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    Reservation,
    ShowSession,
)
from product.serializers import (
    PlanetariumDomeSerializer,
    ShowThemeSerializer,
    AstronomyShowSerializer,
    ReservationSerializer,
    ShowSessionSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        else:
            return AstronomyShowSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        if self.action in "list":
            queryset = (
                queryset
                .select_related()
                .annotate(tickets_available=F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row") - Count("tickets"))
            )
        if self.action == "retrieve":
            queryset = queryset.select_related()

        return queryset


class ResevationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ResevationPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
