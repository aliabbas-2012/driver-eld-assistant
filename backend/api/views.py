from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Carrier, Driver, Trip, Vehicle
from .routing import LatLng, geocode, route_driving
from .serializers import (
    CarrierSerializer,
    DriverSerializer,
    GeocodeSerializer,
    HoursSerializer,
    RegisterSerializer,
    RouteSerializer,
    TripPlanSerializer,
    TripSerializer,
    VehicleSerializer,
)
from .trip_service import create_planned_trip


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "driver-eld-assistant-api"})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        driver = ser.save()
        return Response(
            {"message": "Registration successful.", "driver": DriverSerializer(driver).data},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = getattr(request.user, "driver_profile", None)
        if not driver:
            return Response(
                {"detail": "No driver profile."},
                status=status.HTTP_404_NOT_FOUND,
            )
        u = request.user
        return Response(
            {
                "user": {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                },
                "driver": DriverSerializer(driver).data,
            },
        )


class CarrierListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


class GeocodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = GeocodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        loc = geocode(ser.validated_data["address"])
        return Response({"lat": loc.lat, "lng": loc.lng})


class RouteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = RouteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        a = geocode(d["current_location"])
        b = geocode(d["pickup_location"])
        c = geocode(d["dropoff_location"])
        rt = route_driving(LatLng(a.lat, a.lng), LatLng(b.lat, b.lng), LatLng(c.lat, c.lng))
        return Response(
            {
                "distance_miles": round(rt["distance_miles"], 2),
                "duration_seconds": rt["duration_seconds"],
                "geometry": rt["coordinates"],
                "leg_miles": [round(x, 2) for x in rt.get("leg_miles", [])],
                "instructions": rt.get("instructions") or [],
            },
        )


class HoursView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = HoursSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        used = float(ser.validated_data["cycle_used_hours"])
        add = float(ser.validated_data.get("additional_on_duty_hours") or 0)
        remaining = max(0.0, 70.0 - used - add)
        return Response(
            {
                "limit_hours": 70,
                "cycle_used_hours": used,
                "additional_on_duty_hours": add,
                "on_duty_remaining_approx": round(remaining, 2),
                "hos_schedule": "70/8 property",
            },
        )


class TripPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver = getattr(request.user, "driver_profile", None)
        if not driver:
            return Response({"detail": "No driver profile."}, status=404)
        ser = TripPlanSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            trip = create_planned_trip(
                driver=driver,
                vehicle_id=d.get("vehicle_id"),
                trailer_id=d.get("trailer_id"),
                current_location=d["current_location"],
                pickup_location=d["pickup_location"],
                dropoff_location=d["dropoff_location"],
                cycle_used_hours=d["cycle_used_hours"],
                trip_start_date=d["trip_start_date"],
                shipping_doc=d.get("shipping_doc_number") or "",
                shipper_name=d.get("shipper_name") or "",
                commodity=d.get("commodity") or "",
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"Planning failed: {e!s}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        # Reload with nested prefetch so the 201 body matches GET /trips/<id>/ (daily_logs + duty_changes).
        trip = Trip.objects.prefetch_related(
            "daily_logs__duty_changes",
            "daily_logs__fuel_stops",
        ).get(pk=trip.pk)
        return Response(
            TripSerializer(trip).data,
            status=status.HTTP_201_CREATED,
        )


class TripListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer

    def get_queryset(self):
        drv = getattr(self.request.user, "driver_profile", None)
        if not drv:
            return Trip.objects.none()
        return Trip.objects.filter(driver=drv).prefetch_related(
            "daily_logs__duty_changes",
            "daily_logs__fuel_stops",
        )


class TripDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TripSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drv = getattr(self.request.user, "driver_profile", None)
        if not drv:
            return Trip.objects.none()
        return Trip.objects.filter(driver=drv).prefetch_related(
            "daily_logs__duty_changes",
            "daily_logs__fuel_stops",
        )


class VehicleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleSerializer

    def get_queryset(self):
        drv = getattr(self.request.user, "driver_profile", None)
        if not drv or not drv.carrier_id:
            return Vehicle.objects.none()
        return Vehicle.objects.filter(carrier_id=drv.carrier_id)
