from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Carrier, Trip
from .serializers import (
    CarrierSerializer,
    DriverSerializer,
    RegisterSerializer,
    TripSerializer,
    TripWriteSerializer,
)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {"status": "ok", "service": "driver-eld-assistant-api"},
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        driver = ser.save()
        return Response(
            {
                "message": "Registration successful.",
                "driver": DriverSerializer(driver).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = getattr(request.user, "driver_profile", None)
        if not driver:
            return Response(
                {"detail": "No driver profile linked to this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        u = request.user
        return Response(
            {
                "user": {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                },
                "driver": DriverSerializer(driver).data,
            },
        )


class CarrierListView(generics.ListAPIView):
    """Public list so registration forms can pick carrier_id."""

    permission_classes = [AllowAny]
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


class TripListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        driver = getattr(self.request.user, "driver_profile", None)
        if not driver:
            return Trip.objects.none()
        return Trip.objects.filter(driver=driver).prefetch_related(
            "stops",
            "daily_logs__duty_changes",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TripWriteSerializer
        return TripSerializer

    def perform_create(self, serializer):
        driver = self.request.user.driver_profile
        serializer.save(driver=driver, status=Trip.Status.PLANNED)


class TripDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        driver = getattr(self.request.user, "driver_profile", None)
        if not driver:
            return Trip.objects.none()
        return Trip.objects.filter(driver=driver).prefetch_related(
            "stops",
            "daily_logs__duty_changes",
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return TripWriteSerializer
        return TripSerializer


