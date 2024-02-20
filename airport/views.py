from django.db.models import F, Count
from rest_framework import viewsets

from airport.models import (
    Airport,
    Order,
    AirplaneType,
    Crew,
    Route,
    Airplane,
    Flight,
)
from airport.serializers import (
    AirportSerializer,
    OrderSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    RouteSerializer,
    AirplaneSerializer,
    FlightSerializer,
    RouteListSerializer,
    AirplaneListSerializer,
    FlightListSerializer,
    RouteDetailSerializer,
    AirplaneDetailSerializer,
    FlightDetailSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(
                source__name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )
        if source and destination:
            queryset = queryset.filter(
                source__name__icontains=source,
                destination__name__icontains=destination
            )

        if self.action in ("list", "retrieve"):
            queryset.select_related("source_id", "destination_id")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @staticmethod
    def _params_to_int(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        airplane_type = self.request.query_params.get("airplane_type")
        if airplane_type:
            airplane_type_ids = self._params_to_int(airplane_type)
            queryset = queryset.filter(
                airplane_type__id__in=airplane_type_ids
            )

        if self.action in ("list", "retrieve"):
            queryset.select_related("airplane_type")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = (
                queryset
                .select_related("airplane", "route")
                .prefetch_related("crew")
                .annotate(tickets_available=F(
                    "airplane__rows") * F(
                    "airplane__seats_in_rows") - Count(
                    "tickets"))
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
