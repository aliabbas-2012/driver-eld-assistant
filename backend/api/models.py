"""
ORM aligned with database/driver_eld_assitant_all.sql (PostgreSQL dump).
Uses Meta.db_table so Django table names match the dump. Django adds nullable
user_id on driver and driver_id on trip for JWT ownership (not in original dump).
"""

from django.conf import settings
from django.db import models


class Carrier(models.Model):
    name = models.CharField(max_length=200)
    main_office_address = models.CharField(max_length=500)
    home_terminal_address = models.CharField(max_length=500)
    usdot_number = models.CharField(max_length=20, blank=True)
    mc_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hos_schedule = models.CharField(max_length=10, default="70/8")

    class Meta:
        db_table = "carrier"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Driver(models.Model):
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="drivers",
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    cdl_number = models.CharField(max_length=50)
    license_state = models.CharField(max_length=2)
    hire_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    using_34_restart = models.BooleanField(default=False)

    class Meta:
        db_table = "driver"
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name


class Vehicle(models.Model):
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null=True,
        blank=True,
    )
    truck_number = models.CharField(max_length=50, blank=True)
    license_plate = models.CharField(max_length=20)
    license_state = models.CharField(max_length=2)
    year = models.IntegerField(null=True, blank=True)
    make = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    has_sleeper_berth = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle"
        ordering = ["truck_number"]

    def __str__(self) -> str:
        return self.truck_number or self.license_plate


class Trailer(models.Model):
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="trailers",
        null=True,
        blank=True,
    )
    trailer_number = models.CharField(max_length=50, blank=True)
    license_plate = models.CharField(max_length=20)
    license_state = models.CharField(max_length=2)
    trailer_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trailer"
        ordering = ["trailer_number"]

    def __str__(self) -> str:
        return self.trailer_number or self.license_plate


class Trip(models.Model):
    """Trip row per SQL dump + app fields for HOS planning."""

    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="trips",
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
        help_text="Django extension: who owns this planned trip (JWT).",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
    )
    trailer = models.ForeignKey(
        Trailer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
    )
    current_location = models.CharField(max_length=500)
    current_location_lat = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    current_location_lng = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    pickup_location = models.CharField(max_length=500)
    pickup_location_lat = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    pickup_location_lng = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    dropoff_location = models.CharField(max_length=500)
    dropoff_location_lat = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    dropoff_location_lng = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    total_distance_miles = models.IntegerField(null=True, blank=True)
    total_driving_hours = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True
    )
    total_days = models.IntegerField(null=True, blank=True)
    trip_start_date = models.DateField(null=True, blank=True)
    trip_end_date = models.DateField(null=True, blank=True)
    cycle_used_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text="Hours already on-duty in rolling 8-day window at trip start.",
    )
    route_geometry_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Decoded OSRM coordinates [[lng,lat], ...].",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Trip {self.pk}: {self.current_location} → {self.dropoff_location}"


class DailyLog(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="daily_logs",
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="daily_logs",
        null=True,
        blank=True,
    )
    day_number = models.IntegerField()
    log_date = models.DateField()
    total_miles_driven = models.IntegerField(default=0)
    starting_odometer = models.IntegerField(null=True, blank=True)
    ending_odometer = models.IntegerField(null=True, blank=True)
    driving_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    on_duty_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    off_duty_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    sleeper_berth_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    thirty_min_break_taken = models.BooleanField(default=False)
    thirty_min_break_time = models.TimeField(null=True, blank=True)
    rolling_8day_total = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    hours_remaining_70 = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    using_split_sleeper = models.BooleanField(default=False)
    split_sleeper_first_period = models.JSONField(null=True, blank=True)
    split_sleeper_second_period = models.JSONField(null=True, blank=True)
    log_grid_data = models.JSONField(default=dict, blank=True)
    shipping_doc_number = models.CharField(max_length=100, blank=True)
    shipper_name = models.CharField(max_length=200, blank=True)
    commodity = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)
    driver_signature = models.CharField(max_length=200, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "daily_log"
        ordering = ["log_date", "day_number"]

    def __str__(self) -> str:
        return f"Log {self.log_date} trip={self.trip_id}"


class DutyStatusChange(models.Model):
    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="duty_changes",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    location = models.CharField(max_length=500)
    location_lat = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    location_lng = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    remarks = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "duty_status_change"
        ordering = ["daily_log", "id"]

    def __str__(self) -> str:
        return f"{self.status} {self.start_time}-{self.end_time}"


class FuelStop(models.Model):
    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="fuel_stops",
        null=True,
        blank=True,
    )
    location = models.CharField(max_length=500)
    gallons = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    odometer_reading = models.IntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fuel_stop"
        ordering = ["daily_log", "id"]

    def __str__(self) -> str:
        return self.location
