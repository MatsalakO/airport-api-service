from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airport,
    Order,
    AirplaneType,
    Crew,
    Route,
    Airplane,
    Flight,
    Ticket
)


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_rows", "airplane_type")


class AirplaneImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Airplane
        fields = ("id", "image",)


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_rows,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketFlightSerializer(TicketSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat",)


class AirplaneFlightSerializer(AirplaneSerializer):
    airplane_type_name = serializers.CharField(source="airplane_type.name", read_only=True)

    class Meta:
        model = Airplane
        fields = ("name", "capacity", "airplane_type_name")


class RouteFlightSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("source", "destination", "distance")


class FlightListSerializer(FlightSerializer):
    route = RouteFlightSerializer(many=False, read_only=True)
    airplane = AirplaneFlightSerializer(many=False, read_only=True)
    crew = serializers.SlugRelatedField(slug_field="full_name", many=True, read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time",
                  "arrival_time", "crew", "tickets_available")


class FlightDetailSerializer(FlightSerializer):
    route = RouteFlightSerializer(many=False, read_only=True)
    airplane = AirplaneFlightSerializer(many=False, read_only=True)
    crew = serializers.SlugRelatedField(slug_field="full_name", many=True, read_only=True)
    tickets = TicketFlightSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "tickets")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)
