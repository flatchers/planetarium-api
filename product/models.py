from django.db import models, transaction

from service import settings


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} (rows: {self.rows}, seats: {self.seats_in_row})"


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    show_theme = models.ManyToManyField(ShowTheme)

    def __str__(self):
        return f"title: {self.title}, theme: {self.show_theme}"


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
        unique_together = ("row", "seat", "show_session")
        ordering = ["show_session"]

    def __str__(self):
        return f"{self.row}, {self.seat}, {self.show_session}, {self.reservation}"
