from django.contrib import admin

from .models import (
    Carrier,
    CycleDay,
    DailyLog,
    Driver,
    DutyChange,
    Trip,
    TripStop,
    Vehicle,
)


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "main_office_city", "main_office_state")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user", "carrier", "license_state")
    raw_id_fields = ("user", "carrier")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "tractor_number", "carrier")


class TripStopInline(admin.TabularInline):
    model = TripStop
    extra = 0


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "status", "total_route_miles", "created_at")
    raw_id_fields = ("driver", "vehicle")
    inlines = [TripStopInline]


class DutyChangeInline(admin.TabularInline):
    model = DutyChange
    extra = 0


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "log_date", "timezone")
    inlines = [DutyChangeInline]


@admin.register(CycleDay)
class CycleDayAdmin(admin.ModelAdmin):
    list_display = ("id", "driver", "day_date", "on_duty_hours")
