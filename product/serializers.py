from rest_framework import serializers

from product.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    Reservation,
    Ticket,
    ShowSession
)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    num_seats = serializers.IntegerField(source="capacity")

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "num_seats")


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "show_theme")


class AstronomyShowListSerializer(AstronomyShowSerializer):
    show_theme = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
     )


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    show_theme = ShowThemeSerializer(many=True, read_only=True)


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show_title = serializers.CharField(source="astronomy_show.title", read_only=True)
    planetarium_dome_name = serializers.CharField(source="planetarium_dome.name", read_only=True)
    planetarium_dome_capacity = serializers.CharField(source="planetarium_dome.num_seats", read_only=True)
    taken_tickets = serializers.IntegerField(source="tickets.count", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "astronomy_show_title",
            "planetarium_dome_name",
            "planetarium_dome_capacity",
            "taken_tickets",
            "tickets_available",
            "show_time",
        )


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowDetailSerializer(many=False, read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets",
    )

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time", "taken_seats")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")

    def validate(self, attrs):
        if not (1 <= attrs["row"] <= attrs["show_session"].planetarium_dome.num_seats):
            raise serializers.ValidationError(
                {
                    "seat": f"The seat number must be between 1 and {attrs['show_session'].planetarium_dome.num_seats}"
                }
            )


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "created", "tickets")

