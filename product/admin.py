from django.contrib import admin

from product.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    Reservation,
    Ticket
)

admin.site.register(PlanetariumDome)
admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(Reservation)
admin.site.register(Ticket)
