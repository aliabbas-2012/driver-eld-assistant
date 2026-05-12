from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from .models import (
    Carrier,
    DailyLog,
    Driver,
    DutyStatusChange,
    FuelStop,
    Trailer,
    Trip,
    Vehicle,
)


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = (
            "id",
            "name",
            "main_office_address",
            "home_terminal_address",
            "usdot_number",
            "mc_number",
            "hos_schedule",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            "id",
            "carrier",
            "truck_number",
            "license_plate",
            "license_state",
            "year",
            "make",
            "model",
            "has_sleeper_berth",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TrailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trailer
        fields = (
            "id",
            "carrier",
            "trailer_number",
            "license_plate",
            "license_state",
            "trailer_type",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Driver
        fields = (
            "id",
            "user",
            "username",
            "carrier",
            "first_name",
            "last_name",
            "cdl_number",
            "license_state",
            "hire_date",
            "using_34_restart",
            "created_at",
        )
        read_only_fields = ("id", "user", "created_at")


class DutyStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyStatusChange
        fields = (
            "id",
            "status",
            "start_time",
            "end_time",
            "duration_hours",
            "location",
            "location_lat",
            "location_lng",
            "remarks",
        )


class FuelStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelStop
        fields = (
            "id",
            "location",
            "gallons",
            "cost",
            "odometer_reading",
            "start_time",
            "end_time",
        )


class DailyLogSerializer(serializers.ModelSerializer):
    duty_changes = DutyStatusChangeSerializer(many=True, read_only=True)
    fuel_stops = FuelStopSerializer(many=True, read_only=True)

    class Meta:
        model = DailyLog
        fields = (
            "id",
            "day_number",
            "log_date",
            "total_miles_driven",
            "starting_odometer",
            "ending_odometer",
            "driving_hours",
            "on_duty_hours",
            "off_duty_hours",
            "sleeper_berth_hours",
            "thirty_min_break_taken",
            "thirty_min_break_time",
            "rolling_8day_total",
            "hours_remaining_70",
            "log_grid_data",
            "shipping_doc_number",
            "shipper_name",
            "commodity",
            "remarks",
            "duty_changes",
            "fuel_stops",
        )


class TripSerializer(serializers.ModelSerializer):
    daily_logs = DailyLogSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "carrier",
            "driver",
            "vehicle",
            "trailer",
            "current_location",
            "current_location_lat",
            "current_location_lng",
            "pickup_location",
            "pickup_location_lat",
            "pickup_location_lng",
            "dropoff_location",
            "dropoff_location_lat",
            "dropoff_location_lng",
            "total_distance_miles",
            "total_driving_hours",
            "total_days",
            "trip_start_date",
            "trip_end_date",
            "cycle_used_hours",
            "route_geometry_json",
            "route_instructions_json",
            "created_at",
            "updated_at",
            "daily_logs",
        )
        read_only_fields = ("id", "driver", "created_at", "updated_at", "daily_logs")


class GeocodeSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=500)


class RouteSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=500)
    pickup_location = serializers.CharField(max_length=500)
    dropoff_location = serializers.CharField(max_length=500)


class HoursSerializer(serializers.Serializer):
    cycle_used_hours = serializers.DecimalField(max_digits=5, decimal_places=1)
    additional_on_duty_hours = serializers.DecimalField(
        max_digits=5, decimal_places=1, required=False,
    )


class TripPlanSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=500)
    pickup_location = serializers.CharField(max_length=500)
    dropoff_location = serializers.CharField(max_length=500)
    cycle_used_hours = serializers.DecimalField(max_digits=5, decimal_places=1)
    trip_start_date = serializers.DateField()
    vehicle_id = serializers.IntegerField(required=False, allow_null=True)
    trailer_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_doc_number = serializers.CharField(
        max_length=100, required=False, default="",
    )
    shipper_name = serializers.CharField(max_length=200, required=False, default="")
    commodity = serializers.CharField(max_length=200, required=False, default="")


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    cdl_number = serializers.CharField(max_length=50)
    license_state = serializers.CharField(max_length=2)
    carrier_id = serializers.IntegerField(required=False, allow_null=True)
    carrier = CarrierSerializer(required=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."},
            )
        cid = attrs.get("carrier_id")
        cdata = attrs.get("carrier")
        if cid and cdata:
            raise serializers.ValidationError(
                "Provide either carrier_id or carrier, not both.",
            )
        if not cid and not cdata:
            raise serializers.ValidationError(
                "Provide carrier_id or nested carrier.",
            )
        if cdata:
            cs = CarrierSerializer(data=cdata)
            cs.is_valid(raise_exception=True)
            attrs["_carrier_create"] = cs.validated_data
        return attrs

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("carrier", None)
        carrier_create = validated_data.pop("_carrier_create", None)
        carrier_id = validated_data.pop("carrier_id", None)
        password = validated_data.pop("password")
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        if carrier_id:
            try:
                carrier = Carrier.objects.get(pk=carrier_id)
            except Carrier.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"carrier_id": "Carrier not found."},
                ) from exc
        else:
            carrier = Carrier.objects.create(**carrier_create)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        driver = Driver.objects.create(
            user=user,
            carrier=carrier,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            cdl_number=validated_data["cdl_number"],
            license_state=validated_data["license_state"].upper(),
        )
        return driver
