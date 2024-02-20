from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    OrderViewSet,
    AirplaneTypeViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    AirplaneViewSet,
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("orders", OrderViewSet)
router.register("airplanes-type", AirplaneTypeViewSet)
router.register("crew", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
