from django.contrib import admin

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


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hos_schedule", "created_at")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "carrier", "user")
    raw_id_fields = ("user", "carrier")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "truck_number", "carrier")


@admin.register(Trailer)
class TrailerAdmin(admin.ModelAdmin):
    list_display = ("id", "trailer_number", "carrier")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "total_distance_miles", "trip_start_date", "created_at")
    raw_id_fields = ("carrier", "driver", "vehicle", "trailer")


class DutyInline(admin.TabularInline):
    model = DutyStatusChange
    extra = 0


class FuelInline(admin.TabularInline):
    model = FuelStop
    extra = 0


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "log_date", "day_number")
    inlines = [DutyInline, FuelInline]
