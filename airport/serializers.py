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


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


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

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_rows", "airplane_type")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FlightSerializer):
    route_source = serializers.CharField(source="route.source", read_only=True)
    route_destination = serializers.CharField(source="route.destination", read_only=True)
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(source="airplane.capacity", read_only=True)
    crew = serializers.SlugRelatedField(slug_field="full_name", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route_source", "route_destination", "airplane_name",
                  "airplane_capacity", "departure_time", "arrival_time", "crew")


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class FlightTicketSerializer(FlightSerializer):
    crew = serializers.SlugRelatedField(slug_field="full_name", many=True, read_only=True)
    route_distance = serializers.IntegerField(source="route.distance")
    airplane = serializers.ReadOnlyField(source="airplane.__str__")

    class Meta:
        model = Flight
        fields = ("crew", "route_distance", "airplane")


class TicketListSerializer(TicketSerializer):
    flight_route = serializers.StringRelatedField(source="flight.route", many=False, read_only=True)
    flight = FlightTicketSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight_route", "flight", "order")


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)

