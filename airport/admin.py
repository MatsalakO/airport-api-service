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


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for i in range(1, 6):
            Ticket.objects.create(
                seat=i,
                row=1,
                flight=obj.flights.first(),
                order=obj
            )


admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(Order)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
