from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Airport,
    Order,
    AirplaneType,
    Crew,
    Route,
    Airplane,
    Flight,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirportSerializer,
    OrderSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    RouteSerializer,
    AirplaneSerializer,
    FlightSerializer,
    RouteListSerializer,
    FlightListSerializer,
    RouteDetailSerializer,
    FlightDetailSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
    AirplaneListSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = (
                queryset
                .prefetch_related(
                    "tickets",
                    "tickets__flight",
                    "tickets__order",
                    "tickets__flight__airplane",
                    "tickets__flight__crew",
                    "tickets__flight__route__source",
                )
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "string"}},
                description="Fiter by source name"
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "string"}},
                description="Fiter by destination name"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image", permission_classes=(IsAdminUser,))
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_type",
                type={"type": "list", "items": {"type": "number"}},
                description="Fiter by airplane type id`s"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
