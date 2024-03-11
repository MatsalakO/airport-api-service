from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import (
    Crew,
    Route,
    Airplane,
    Airport,
    AirplaneType
)

FLIGHT_URL = reverse("airport:flight-list")


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@email.com", "testpass"
        )
        self.client.force_authenticate(self.user)
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

        self.source_airport = Airport.objects.create(
            name="Source", closest_big_city="Source City"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination", closest_big_city="Destination City"
        )

        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=100,
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_rows=6,
            airplane_type=AirplaneType.objects.create(name="Test Type"),
        )

    def test_flight_creation_forbidden(self):
        response = self.client.post(
            FLIGHT_URL,
            {
                "crew": [self.crew.id],
                "route": self.route.id,
                "airplane": self.airplane.id,
                "departure_time": "2024-02-10T12:00:00Z",
                "arrival_time": "2024-02-10T14:00:00Z",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_list(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminFlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@email.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

        self.source_airport = Airport.objects.create(
            name="Source", closest_big_city="Source City"
        )
        self.destination_airport = Airport.objects.create(
            name="Destination", closest_big_city="Destination City"
        )

        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=100,
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_rows=6,
            airplane_type=AirplaneType.objects.create(name="Test Type"),
        )

    def test_flight_creation(self):
        response = self.client.post(
            FLIGHT_URL,
            {
                "crew": [self.crew.id],
                "route": self.route.id,
                "airplane": self.airplane.id,
                "departure_time": "2024-02-10T12:00:00Z",
                "arrival_time": "2024-02-10T14:00:00Z",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
