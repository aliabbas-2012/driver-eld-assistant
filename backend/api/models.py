from django.conf import settings
from django.db import models


class Carrier(models.Model):
    """Motor carrier (log sheet header fields per FMCSA record-of-duty guidance)."""

    name = models.CharField(max_length=255)
    main_office_street = models.CharField(max_length=255)
    main_office_city = models.CharField(max_length=100)
    main_office_state = models.CharField(max_length=2)
    main_office_zip = models.CharField(max_length=20)
    home_terminal_street = models.CharField(max_length=255)
    home_terminal_city = models.CharField(max_length=100)
    home_terminal_state = models.CharField(max_length=2)
    home_terminal_zip = models.CharField(max_length=20)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Driver(models.Model):
    """
    Driver profile linked 1:1 to Django auth User (login identity).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="drivers",
    )
    full_name = models.CharField(max_length=255)
    co_driver_name = models.CharField(max_length=255, blank=True)
    license_state = models.CharField(max_length=2)
    license_number = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name


class Vehicle(models.Model):
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )
    tractor_number = models.CharField(max_length=64)
    tractor_plate = models.CharField(max_length=32)
    tractor_plate_state = models.CharField(max_length=2)
    trailer_number = models.CharField(max_length=64)
    trailer_plate = models.CharField(max_length=32)
    trailer_plate_state = models.CharField(max_length=2)

    class Meta:
        ordering = ["tractor_number"]

    def __str__(self) -> str:
        return f"{self.tractor_number} ({self.tractor_plate_state})"


class Trip(models.Model):
    """
    Planned / computed trip (current -> pickup -> dropoff).
    Coordinates optional until geocode step fills them.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PLANNED = "planned", "Planned"
        DEMO_SEEDED = "demo_seeded", "Demo seeded"

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="trips",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="trips",
    )
    current_location = models.TextField()
    pickup_location = models.TextField()
    dropoff_location = models.TextField()
    current_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    current_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    pickup_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    pickup_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    dropoff_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    dropoff_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    miles_current_to_pickup = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    miles_pickup_to_dropoff = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    total_route_miles = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    estimated_driving_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    cycle_used_hours_8day = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="On-duty hours already used in rolling 8-day window (70h/8 property).",
    )
    assumed_avg_mph = models.DecimalField(
        max_digits=5, decimal_places=2, default=55,
    )
    daily_start_local_time = models.CharField(max_length=5, default="06:00")
    timezone = models.CharField(max_length=64, default="America/Chicago")
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    shipping_document_number = models.CharField(max_length=128, blank=True)
    shipper_name = models.CharField(max_length=255, blank=True)
    commodity = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Trip {self.pk} ({self.driver.full_name})"


class TripStop(models.Model):
    """Ordered stops (start, pickup, fuel, break, dropoff, etc.)."""

    class StopType(models.TextChoices):
        START = "start", "Start"
        PICKUP = "pickup", "Pickup"
        FUEL = "fuel", "Fuel"
        BREAK = "break", "Break"
        DROPOFF = "dropoff", "Dropoff"
        REST = "rest", "Rest"
        OTHER = "other", "Other"

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="stops",
    )
    seq = models.PositiveIntegerField()
    stop_type = models.CharField(max_length=32, choices=StopType.choices)
    place_name = models.CharField(max_length=255)
    address = models.TextField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    planned_arrive_local = models.CharField(max_length=32, blank=True)
    planned_depart_local = models.CharField(max_length=32, blank=True)
    dwell_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["trip", "seq"]
        unique_together = [["trip", "seq"]]

    def __str__(self) -> str:
        return f"{self.trip_id}:{self.seq} {self.stop_type}"


class DailyLog(models.Model):
    """
    One log per calendar day (graph grid + totals per FMCSA driver log).
    """

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="daily_logs",
    )
    log_date = models.DateField()
    timezone = models.CharField(max_length=64)
    total_miles_driving = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
    )
    odometer_start = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    odometer_end = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    total_on_duty_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
    )
    signature_line = models.CharField(
        max_length=255,
        default="Signed on file (demo)",
    )

    class Meta:
        ordering = ["log_date"]
        unique_together = [["trip", "log_date"]]

    def __str__(self) -> str:
        return f"{self.log_date} (trip {self.trip_id})"


class DutyChange(models.Model):
    """
    Duty status change line (remarks / location align with FMCSA guide).
    Status values match graph rows: off duty, sleeper, driving, on-duty N/D.
    """

    class DutyStatus(models.TextChoices):
        OFF_DUTY = "off_duty", "Off Duty"
        SLEEPER = "sleeper", "Sleeper Berth"
        DRIVING = "driving", "Driving"
        ON_DUTY_NOT_DRIVING = "on_duty_not_driving", "On Duty (Not Driving)"

    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="duty_changes",
    )
    changed_at_local = models.CharField(max_length=32)
    duty_status = models.CharField(max_length=32, choices=DutyStatus.choices)
    location_remark = models.TextField()
    seq = models.PositiveIntegerField()

    class Meta:
        ordering = ["daily_log", "seq"]
        unique_together = [["daily_log", "seq"]]

    def __str__(self) -> str:
        return f"{self.duty_status} @ {self.changed_at_local}"


class CycleDay(models.Model):
    """Rolling window on-duty hours per calendar day (70-hour / 8-day property)."""

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="cycle_days",
    )
    day_date = models.DateField()
    on_duty_hours = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["day_date"]
        unique_together = [["driver", "day_date"]]

    def __str__(self) -> str:
        return f"{self.driver_id} {self.day_date}: {self.on_duty_hours}h"
