from rest_framework import serializers

from airport.models import Airport, Order, AirplaneType, Crew, Route, Airplane, Flight


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


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_rows", "airplane_type")


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ("id", "row", "seat", "flight", "order")
