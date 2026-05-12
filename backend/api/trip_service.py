"""Create Trip + DailyLog + DutyStatusChange + FuelStop from HOS plan."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction

from .hos_plan import day_totals, log_grid_json, plan_trip
from .models import DailyLog, Driver, DutyStatusChange, FuelStop, Trailer, Trip, Vehicle
from .routing import LatLng, geocode, route_driving


def _time_from_float(h: float):
    from datetime import time as dtime

    h = h % 24.0
    hh = int(h)
    mm = int(round((h - hh) * 60)) % 60
    return dtime(hh, mm)


@transaction.atomic
def create_planned_trip(
    *,
    driver: Driver,
    vehicle_id: int | None,
    trailer_id: int | None,
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    cycle_used_hours: Decimal,
    trip_start_date: date,
    shipping_doc: str,
    shipper_name: str,
    commodity: str,
) -> Trip:
    cur = geocode(current_location)
    pik = geocode(pickup_location)
    drp = geocode(dropoff_location)
    rt = route_driving(
        LatLng(cur.lat, cur.lng),
        LatLng(pik.lat, pik.lng),
        LatLng(drp.lat, drp.lng),
    )
    total_miles = float(rt["distance_miles"])
    leg_miles = rt.get("leg_miles") or [0.0, total_miles]
    miles_to_pickup = float(leg_miles[0]) if leg_miles else 0.0

    days, summary = plan_trip(
        total_miles=total_miles,
        miles_to_pickup=miles_to_pickup,
        trip_start=trip_start_date,
        current_label=current_location[:200],
        pickup_label=pickup_location[:200],
        dropoff_label=dropoff_location[:200],
        cycle_used=float(cycle_used_hours),
    )

    v_id = vehicle_id
    t_id = trailer_id
    if driver.carrier_id:
        if v_id and not Vehicle.objects.filter(pk=v_id, carrier_id=driver.carrier_id).exists():
            raise ValueError("vehicle_id must belong to your carrier.")
        if t_id and not Trailer.objects.filter(pk=t_id, carrier_id=driver.carrier_id).exists():
            raise ValueError("trailer_id must belong to your carrier.")

    trip = Trip.objects.create(
        carrier=driver.carrier,
        driver=driver,
        vehicle_id=v_id,
        trailer_id=t_id,
        current_location=current_location[:500],
        current_location_lat=Decimal(str(round(cur.lat, 8))),
        current_location_lng=Decimal(str(round(cur.lng, 8))),
        pickup_location=pickup_location[:500],
        pickup_location_lat=Decimal(str(round(pik.lat, 8))),
        pickup_location_lng=Decimal(str(round(pik.lng, 8))),
        dropoff_location=dropoff_location[:500],
        dropoff_location_lat=Decimal(str(round(drp.lat, 8))),
        dropoff_location_lng=Decimal(str(round(drp.lng, 8))),
        total_distance_miles=int(round(total_miles)),
        total_driving_hours=Decimal(str(round(total_miles / 55.0, 1))),
        total_days=len(days),
        trip_start_date=trip_start_date,
        trip_end_date=days[-1].log_date if days else trip_start_date,
        cycle_used_hours=Decimal(str(cycle_used_hours)),
        route_geometry_json={"type": "LineString", "coordinates": rt["coordinates"]},
        route_instructions_json={
            "driving_steps": rt.get("instructions") or [],
            "hos_stops": summary.get("map_stops") or [],
            "hos_summary": {
                "total_miles": summary.get("total_miles"),
                "total_drive_hours": summary.get("total_drive_hours"),
                "days": summary.get("days"),
                "cycle_used_start": summary.get("cycle_used_start"),
                "hours_remaining_70_approx": summary.get("hours_remaining_70_approx"),
            },
        },
    )

    for day in days:
        totals = day_totals(day.segments)
        miles_day = sum(s.miles for s in day.segments if s.status == "driving")
        thirty = any(
            s.status == "off_duty" and "30-minute" in s.location for s in day.segments
        )
        brk_t = next(
            (_time_from_float(s.start_h) for s in day.segments if "30-minute" in s.location),
            None,
        )
        log = DailyLog.objects.create(
            trip=trip,
            driver=driver,
            day_number=day.day_number,
            log_date=day.log_date,
            total_miles_driven=int(round(miles_day)),
            driving_hours=totals["driving_hours"],
            on_duty_hours=totals["on_duty_hours"],
            off_duty_hours=totals["off_duty_hours"],
            sleeper_berth_hours=totals["sleeper_berth_hours"],
            thirty_min_break_taken=thirty,
            thirty_min_break_time=brk_t,
            rolling_8day_total=Decimal("0"),
            hours_remaining_70=Decimal(str(summary.get("hours_remaining_70_approx", 0))),
            log_grid_data=log_grid_json(day.segments),
            shipping_doc_number=shipping_doc[:100],
            shipper_name=shipper_name[:200],
            commodity=commodity[:200],
            remarks=" | ".join(
                f"{_time_from_float(s.start_h)} {s.status}" for s in day.segments[:16]
            )[:5000],
        )
        for s in day.segments:
            DutyStatusChange.objects.create(
                daily_log=log,
                status=s.status,
                start_time=_time_from_float(s.start_h),
                end_time=_time_from_float(s.end_h),
                duration_hours=Decimal(str(round(s.end_h - s.start_h, 2))),
                location=s.location[:500],
            )
            if s.status == "on_duty_not_driving" and "Fuel" in s.location:
                FuelStop.objects.create(
                    daily_log=log,
                    location=s.location[:500],
                    start_time=_time_from_float(s.start_h),
                    end_time=_time_from_float(s.end_h),
                )

    trip.save(update_fields=["updated_at"])
    return trip
