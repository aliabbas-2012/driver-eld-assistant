"""
Property HOS (70/8 baseline) — simplified trip-day builder for demo accuracy.
Rules applied: 55 mph, 06:00 work start, 00–06 off, 30m pre-trip, 11h max drive/day,
14h on-duty window from first on-duty, 30m break after 8h driving, fuel 30m every 1000 mi,
pickup 1h ODND after reaching pickup leg, dropoff 1h + 15m post-trip last day.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from decimal import Decimal
from typing import Any


AVG_MPH = 55.0
PRE_TRIP = 0.5
POST_TRIP = 0.25
PICKUP = 1.0
DROPOFF = 1.0
FUEL = 0.5
BREAK = 0.5
MAX_DRIVE = 11.0
MAX_WINDOW = 14.0
NIGHT_OFF = 6.0  # midnight–06:00


@dataclass
class Seg:
    status: str
    start_h: float
    end_h: float
    location: str
    miles: float = 0.0


@dataclass
class DayPlan:
    log_date: date
    day_number: int
    segments: list[Seg] = field(default_factory=list)


def _add(seg_list: list[Seg], st: str, sh: float, eh: float, loc: str, miles: float = 0.0) -> float:
    if eh <= sh + 1e-6:
        return sh
    seg_list.append(Seg(st, sh, eh, loc[:500], miles))
    return eh


def _time(h: float) -> time:
    h = h % 24.0
    hh = int(h)
    mm = int(round((h - hh) * 60)) % 60
    return time(hh, mm)


def plan_trip(
    *,
    total_miles: float,
    miles_to_pickup: float,
    trip_start: date,
    current_label: str,
    pickup_label: str,
    dropoff_label: str,
    cycle_used: float = 0.0,
) -> tuple[list[DayPlan], dict[str, Any]]:
    """
    Build day-by-day segments. Driving is consumed in chunks with break/fuel/pickup inserted.
    """
    total_drive_h = total_miles / AVG_MPH
    miles_to_pickup = max(0.0, float(miles_to_pickup))
    drive_h_to_pickup = miles_to_pickup / AVG_MPH if miles_to_pickup > 0 else 0.0
    cumulative_miles = 0.0
    cumulative_drive = 0.0
    drive_since_break = 0.0
    pickup_done = miles_to_pickup <= 0
    map_stops: list[dict[str, Any]] = []
    days: list[DayPlan] = []
    day_idx = 0
    remaining_drive = total_drive_h
    next_fuel_at = 1000.0

    while remaining_drive > 1e-6 or day_idx == 0:
        d = trip_start + timedelta(days=day_idx)
        day = DayPlan(log_date=d, day_number=day_idx + 1)
        segs = day.segments
        h = 0.0
        h = _add(segs, "off_duty", h, NIGHT_OFF, f"{current_label if day_idx == 0 else dropoff_label} — rest")
        window = 0.0
        drive_day = 0.0

        h = _add(
            segs,
            "on_duty_not_driving",
            h,
            h + PRE_TRIP,
            f"{current_label if day_idx == 0 else pickup_label} — Pre-trip",
        )
        window += PRE_TRIP

        def can_drive() -> bool:
            return drive_day < MAX_DRIVE - 1e-6 and window < MAX_WINDOW - 1e-6

        while can_drive() and (remaining_drive > 1e-6 or not pickup_done):
            # Pickup once when cumulative drive reaches drive_h_to_pickup
            if (
                not pickup_done
                and miles_to_pickup > 0
                and cumulative_drive >= drive_h_to_pickup - 1e-6
                and window + PICKUP <= MAX_WINDOW + 1e-6
            ):
                h = _add(
                    segs,
                    "on_duty_not_driving",
                    h,
                    h + PICKUP,
                    f"{pickup_label} — Pickup / loading",
                )
                window += PICKUP
                pickup_done = True
                map_stops.append({"kind": "pickup", "label": pickup_label})
                continue

            if drive_since_break >= 8.0 - 1e-6 and window + BREAK <= MAX_WINDOW + 1e-6:
                h = _add(segs, "off_duty", h, h + BREAK, "30-minute break (FMCSA)")
                window += BREAK
                drive_since_break = 0.0
                map_stops.append({"kind": "break", "label": "30-min break"})
                continue

            if cumulative_miles >= next_fuel_at - 1e-6 and window + FUEL <= MAX_WINDOW + 1e-6:
                h = _add(
                    segs,
                    "on_duty_not_driving",
                    h,
                    h + FUEL,
                    f"Fuel stop — ~mile {int(next_fuel_at)}",
                )
                window += FUEL
                map_stops.append({"kind": "fuel", "label": f"Fuel ~{int(next_fuel_at)} mi"})
                next_fuel_at += 1000.0
                continue

            room_drive = min(MAX_DRIVE - drive_day, MAX_WINDOW - window, remaining_drive)
            if room_drive < 1e-4:
                break
            # split if crossing 8h break mid-chunk
            until_break = max(0.0, 8.0 - drive_since_break)
            chunk = min(room_drive, until_break if until_break > 1e-6 else room_drive)
            if chunk < 1e-4:
                chunk = min(room_drive, BREAK)  # should not happen
            m = chunk * AVG_MPH
            h = _add(
                segs,
                "driving",
                h,
                h + chunk,
                f"Toward {dropoff_label}",
                m,
            )
            window += chunk
            drive_day += chunk
            cumulative_drive += chunk
            cumulative_miles += m
            drive_since_break += chunk
            remaining_drive -= chunk

        if remaining_drive <= 1e-6:
            if window + DROPOFF + POST_TRIP <= MAX_WINDOW + 1e-6:
                h = _add(
                    segs,
                    "on_duty_not_driving",
                    h,
                    h + DROPOFF,
                    f"{dropoff_label} — Dropoff",
                )
                window += DROPOFF
                map_stops.append({"kind": "dropoff", "label": dropoff_label})
                h = _add(
                    segs,
                    "on_duty_not_driving",
                    h,
                    h + POST_TRIP,
                    f"{dropoff_label} — Post-trip",
                )
                window += POST_TRIP
            h = _add(segs, "off_duty", h, 24.0, f"{dropoff_label} — Off duty")
            days.append(day)
            break

        h = _add(segs, "off_duty", h, 24.0, f"{dropoff_label} — End of day reset")
        days.append(day)
        day_idx += 1
        drive_since_break = 0.0
        if day_idx > 90:
            break

    roll = float(cycle_used)
    hrs_rem = max(0.0, 70.0 - roll)
    summary: dict[str, Any] = {
        "total_miles": round(total_miles, 1),
        "total_drive_hours": round(total_drive_h, 2),
        "days": len(days),
        "map_stops": map_stops,
        "cycle_used_start": cycle_used,
        "hours_remaining_70_approx": round(hrs_rem, 1),
    }
    return days, summary


def day_totals(segments: list[Seg]) -> dict[str, Decimal]:
    d = od = off = sb = Decimal("0")
    for s in segments:
        dur = Decimal(str(round(s.end_h - s.start_h, 2)))
        if s.status == "driving":
            d += dur
        elif s.status == "on_duty_not_driving":
            od += dur
        elif s.status == "off_duty":
            off += dur
        elif s.status == "sleeper":
            sb += dur
    return {
        "driving_hours": d,
        "on_duty_hours": od,
        "off_duty_hours": off,
        "sleeper_berth_hours": sb,
    }


def log_grid_json(segments: list[Seg]) -> dict[str, Any]:
    intervals: dict[str, list[dict[str, float]]] = {
        "off_duty": [],
        "sleeper": [],
        "driving": [],
        "on_duty_not_driving": [],
    }
    for s in segments:
        if s.status in intervals:
            intervals[s.status].append({"start_h": s.start_h, "end_h": s.end_h})
    return {"intervals": intervals}
