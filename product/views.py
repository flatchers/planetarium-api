from django.db.models import Count, F
from rest_framework import viewsets, pagination, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from product.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    Reservation,
    ShowSession,
)
from product.permissions import IsAdminAllORIsAuthenticatedReadOnly
from product.serializers import (
    PlanetariumDomeSerializer,
    ShowThemeSerializer,
    AstronomyShowSerializer,
    ReservationSerializer,
    ShowSessionSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer, AstronomyImageSerializer,
)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

    @staticmethod
    def _param_to_int(value):
        return [int(i) for i in value.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        show_themes = self.request.query_params.get("show_themes")

        if show_themes:
            show_themes_ids = self._param_to_int(show_themes)
            queryset = queryset.filter(show_themes__id__in=show_themes_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        if self.action == "upload_image":
            return AstronomyImageSerializer
        else:
            return AstronomyShowSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser,],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        astronomy = self.get_object()
        serializer = AstronomyImageSerializer(astronomy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer
    permission_classes = (IsAdminAllORIsAuthenticatedReadOnly,)

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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
