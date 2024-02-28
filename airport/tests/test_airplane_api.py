from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="Test")
    defaults = {
        "name": "Test",
        "rows": 5,
        "seats_in_rows": 10,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "test")
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        sample_airplane()
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_airplanes_by_types(self):
        airplane1 = sample_airplane(name="Test1")
        airplane2 = sample_airplane(name="Test2")

        airplane_type = AirplaneType.objects.create(name="default")
        airplane3 = sample_airplane(name="Test3", airplane_type=airplane_type)

        res = self.client.get(AIRPLANE_URL, {"airplane_type": f"{airplane_type.id}"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertIn(serializer3.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_retrieve_airplane_detail(self):
        airplane1 = sample_airplane()

        url = detail_url(airplane1.id)
        res = self.client.get(url)

        serializer = AirplaneListSerializer(airplane1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.create(name="Test")
        payload = {
            "name": "test",
            "rows": 5,
            "seats_in_rows": 10,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Test")
        payload = {
            "name": "test",
            "rows": 5,
            "seats_in_rows": 10,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
