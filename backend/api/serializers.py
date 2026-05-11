from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from .models import (
    Carrier,
    DailyLog,
    Driver,
    DutyChange,
    Trip,
    TripStop,
    Vehicle,
)


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = (
            "id",
            "name",
            "main_office_street",
            "main_office_city",
            "main_office_state",
            "main_office_zip",
            "home_terminal_street",
            "home_terminal_city",
            "home_terminal_state",
            "home_terminal_zip",
        )


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            "id",
            "carrier",
            "tractor_number",
            "tractor_plate",
            "tractor_plate_state",
            "trailer_number",
            "trailer_plate",
            "trailer_plate_state",
        )
        read_only_fields = ("id",)


class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Driver
        fields = (
            "id",
            "user",
            "username",
            "email",
            "carrier",
            "full_name",
            "co_driver_name",
            "license_state",
            "license_number",
            "created_at",
        )
        read_only_fields = ("id", "user", "created_at")


class TripStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripStop
        fields = (
            "id",
            "seq",
            "stop_type",
            "place_name",
            "address",
            "lat",
            "lng",
            "planned_arrive_local",
            "planned_depart_local",
            "dwell_minutes",
        )
        read_only_fields = ("id",)


class DutyChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyChange
        fields = (
            "id",
            "changed_at_local",
            "duty_status",
            "location_remark",
            "seq",
        )
        read_only_fields = ("id",)


class DailyLogSerializer(serializers.ModelSerializer):
    duty_changes = DutyChangeSerializer(many=True, read_only=True)

    class Meta:
        model = DailyLog
        fields = (
            "id",
            "log_date",
            "timezone",
            "total_miles_driving",
            "odometer_start",
            "odometer_end",
            "total_on_duty_hours",
            "signature_line",
            "duty_changes",
        )
        read_only_fields = ("id", "duty_changes")


class TripSerializer(serializers.ModelSerializer):
    stops = TripStopSerializer(many=True, read_only=True)
    daily_logs = DailyLogSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "driver",
            "vehicle",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_lat",
            "current_lng",
            "pickup_lat",
            "pickup_lng",
            "dropoff_lat",
            "dropoff_lng",
            "miles_current_to_pickup",
            "miles_pickup_to_dropoff",
            "total_route_miles",
            "estimated_driving_hours",
            "cycle_used_hours_8day",
            "assumed_avg_mph",
            "daily_start_local_time",
            "timezone",
            "status",
            "shipping_document_number",
            "shipper_name",
            "commodity",
            "notes",
            "created_at",
            "stops",
            "daily_logs",
        )
        read_only_fields = (
            "id",
            "driver",
            "created_at",
            "stops",
            "daily_logs",
        )


class TripWriteSerializer(serializers.ModelSerializer):
    """Create/update trip; driver set in view from JWT user."""

    class Meta:
        model = Trip
        fields = (
            "vehicle",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_lat",
            "current_lng",
            "pickup_lat",
            "pickup_lng",
            "dropoff_lat",
            "dropoff_lng",
            "miles_current_to_pickup",
            "miles_pickup_to_dropoff",
            "total_route_miles",
            "estimated_driving_hours",
            "cycle_used_hours_8day",
            "assumed_avg_mph",
            "daily_start_local_time",
            "timezone",
            "status",
            "shipping_document_number",
            "shipper_name",
            "commodity",
            "notes",
        )

    def validate_vehicle(self, vehicle: Vehicle) -> Vehicle:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        driver = getattr(request.user, "driver_profile", None)
        if not driver:
            raise serializers.ValidationError("No driver profile for this user.")
        if vehicle.carrier_id != driver.carrier_id:
            raise serializers.ValidationError(
                "Vehicle must belong to your carrier.",
            )
        return vehicle


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)
    co_driver_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True,
    )
    license_state = serializers.CharField(max_length=2)
    license_number = serializers.CharField(max_length=64)
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
                "Provide carrier_id for an existing carrier or nested carrier to create one.",
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
            full_name=validated_data["full_name"],
            co_driver_name=validated_data.get("co_driver_name") or "",
            license_state=validated_data["license_state"].upper(),
            license_number=validated_data["license_number"],
        )
        return driver

