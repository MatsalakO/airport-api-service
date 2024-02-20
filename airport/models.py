from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Created at {self.created_at} by {self.user}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="route_source"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="route_destination"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_rows = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplane"
    )

    def __str__(self):
        return (f"{self.name} is {self.airplane_type} type and has"
                f"{self.rows * self.seats_in_rows} places")

    @property
    def capacity(self):
        return f"{self.rows * self.seats_in_rows}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flight")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flight")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flight")

    def __str__(self):
        return (f"Flight from {self.route.source} to {self.route.destination}" 
                f"estimated time of arrival {self.arrival_time}")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("seat", "row", "flight")

    def __str__(self):
        return f"{self.flight} {self.seat} {self.row}"

    @staticmethod
    def validate_seat(seat, num_seats, row, num_rows, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise({
                "seat": f"seat must be in  range [1, {num_seats}], not {seat}"
            })
        if not (1 <= row <= num_rows):
            raise error_to_raise({
                "row": f"row must be in  range [1, {num_rows}], not {row}"
            })

    def clean(self):
        Ticket.validate_seat(
            self.seat,
            self.flight.airplane.seats_in_rows,
            self.row,
            self.flight.airplane.rows,
            ValidationError
        )
