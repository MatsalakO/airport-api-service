from django.contrib import admin

from airport.models import (
    Route,
    Airport,
    Order,
    AirplaneType,
    Crew,
    Airplane,
    Flight,
    Ticket
)

admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(Order)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
