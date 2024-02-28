from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer, RouteDetailSerializer


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


ROUTE_URL = reverse("airport:route-list")


def sample_route(**params):
    source = Airport.objects.create(name="Lviv Airport", closest_big_city="Lviv")
    destination = Airport.objects.create(name="Kyiv Airport", closest_big_city="Kyiv")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 400,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "test")
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        route1 = sample_route()
        route2 = sample_route(source=Airport.objects.create(name="Dolyna", closest_big_city="Dolyna"))

        res = self.client.get(ROUTE_URL)

        airplanes = Route.objects.all()
        serializer = RouteListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_routes_by_source(self):
        route1 = sample_route()

        source2 = Airport.objects.create(name="Dolyna", closest_big_city="Dolyna")
        route2 = sample_route(source=source2)

        res = self.client.get(ROUTE_URL, {"source": f"{source2.name}"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_filter_routes_by_destination(self):
        route1 = sample_route()

        destination2 = Airport.objects.create(name="Dolyna", closest_big_city="Dolyna")
        route2 = sample_route(source=destination2)

        res = self.client.get(ROUTE_URL, {"source": f"{destination2.name}"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_route_creation_forbidden(self):
        source = Airport.objects.create(name="Lviv Airport", closest_big_city="Lviv")
        destination = Airport.objects.create(name="Kyiv Airport", closest_big_city="Kyiv")
        response = self.client.post(
            ROUTE_URL,
            {
                "source": source.id,
                "destination": destination.id,
                "distance": 400,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_route_detail(self):
        route1 = sample_route()

        url = detail_url(route1.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_route_creation(self):
        source = Airport.objects.create(name="Dnipro Airport", closest_big_city="Dnipro")
        destination = Airport.objects.create(name="Dolyna", closest_big_city="Dolyna")
        response = self.client.post(
            ROUTE_URL,
            {
                "source": source.id,
                "destination": destination.id,
                "distance": 400,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
