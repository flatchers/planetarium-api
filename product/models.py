import os
import uuid

from django.db import models, transaction
from django.utils.text import slugify
from rest_framework.validators import UniqueTogetherValidator

from service import settings


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def num_seats(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} (rows: {self.rows}, seats: {self.seats_in_row})"


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def create_custom_path(instance, filename: str):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/movies/", filename)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    show_themes = models.ManyToManyField(ShowTheme)
    image = models.ImageField(null=True, upload_to=create_custom_path)

    def __str__(self):
        return f"title: {self.title}, theme: {self.show_themes}"


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="show_sessions")
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE, related_name="show_sessions")
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show}, {self.planetarium_dome} {self.show_time}"


class Reservation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation

    def __str__(self):
        return f"{self.user}, {self.created}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "show_session"],
                name="unique_ticket_row_seat_show_session")
        ]
        ordering = ["show_session"]

    @staticmethod
    def validate(row, seat, show_session, error_to_raise):
        if not (
                (1 <= row <= show_session.planetarium_dome.rows) or
                (1 <= seat <= show_session.planetarium_dome.seats_in_row)
        ):
            raise error_to_raise(
                {
                    "seat": f"The seat number must be between 1 and {show_session.planetarium_dome.num_seats}"
                }
            )

    def clean(self):
        Ticket.validate(self.row, self.seat, self.show_session, ValueError)

    def __str__(self):
        return f"{self.row}, {self.seat}, {self.show_session}, {self.reservation}"
