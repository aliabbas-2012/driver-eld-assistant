"""Geocode (Nominatim) and route (OSRM) — free tier friendly."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


USER_AGENT = "driver-eld-assistant/1.0 (contact: dev@localhost)"
MAX_INSTRUCTIONS = 180


@dataclass
class LatLng:
    lat: float
    lng: float


def _get_json(url: str, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def geocode(address: str) -> LatLng:
    """Single result from Nominatim (respect 1 req/s)."""
    params = urllib.parse.urlencode(
        {"q": address, "format": "json", "limit": "1"},
    )
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    data = _get_json(url)
    time.sleep(1.05)
    if not data:
        raise ValueError(f"No geocode result for: {address}")
    row = data[0]
    return LatLng(lat=float(row["lat"]), lng=float(row["lon"]))


def _step_instruction(step: dict[str, Any]) -> str:
    man = step.get("maneuver") or {}
    ins = man.get("instruction")
    if isinstance(ins, str) and ins.strip():
        return ins.strip()
    typ = str(man.get("type", "")).replace("_", " ").strip()
    mod = str(man.get("modifier", "")).replace("_", " ").strip()
    name = (step.get("name") or "").strip()
    ref = (step.get("ref") or "").strip()
    road = name or ref
    parts: list[str] = []
    if typ and typ != "new name":
        parts.append(typ.title())
    if mod:
        parts.append(mod)
    if road:
        parts.append(f"— {road}")
    out = " ".join(parts).strip()
    return out or "Continue"


def _build_instructions(route: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    legs = route.get("legs") or []
    leg_labels = [
        "Leg 1: Current location → pickup",
        "Leg 2: Pickup → dropoff",
    ]
    for li, leg in enumerate(legs):
        if len(out) >= MAX_INSTRUCTIONS:
            break
        if li < len(leg_labels):
            out.append(
                {
                    "kind": "leg_header",
                    "instruction": leg_labels[li],
                    "distance_m": None,
                },
            )
        for step in leg.get("steps") or []:
            if len(out) >= MAX_INSTRUCTIONS:
                out.append(
                    {
                        "kind": "truncated",
                        "instruction": "(Additional turn-by-turn steps omitted for brevity)",
                        "distance_m": None,
                    },
                )
                return out
            dist_m = float(step.get("distance", 0) or 0)
            out.append(
                {
                    "kind": "driving",
                    "instruction": _step_instruction(step),
                    "distance_m": round(dist_m, 1),
                    "duration_s": float(step.get("duration", 0) or 0),
                },
            )
    return out


def route_driving(
    a: LatLng,
    b: LatLng,
    c: LatLng,
) -> dict[str, Any]:
    """
    OSRM public demo: current → pickup → dropoff.
    Returns distance, duration, GeoJSON coordinates, leg miles, and parsed steps.
    """
    coords = f"{a.lng},{a.lat};{b.lng},{b.lat};{c.lng},{c.lat}"
    q = urllib.parse.urlencode(
        {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true",
        },
    )
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}?{q}"
    try:
        # Public OSRM can be slow on long routes + steps=true; avoid flaky 30s read timeouts.
        data = _get_json(url, timeout=90.0)
    except urllib.error.HTTPError as e:
        raise ValueError(f"OSRM error: {e}") from e
    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError(f"OSRM no route: {data.get('message', data)}")
    route = data["routes"][0]
    geom = route.get("geometry") or {}
    coordinates = geom.get("coordinates") or []
    meters = float(route.get("distance", 0))
    legs = route.get("legs") or []
    leg_miles = []
    for leg in legs[:2]:
        leg_miles.append(float(leg.get("distance", 0)) * 0.000621371)
    instructions = _build_instructions(route)
    return {
        "distance_miles": meters * 0.000621371,
        "duration_seconds": float(route.get("duration", 0)),
        "coordinates": coordinates,
        "leg_miles": leg_miles,
        "instructions": instructions,
    }
