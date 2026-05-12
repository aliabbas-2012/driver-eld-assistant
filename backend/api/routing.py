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


def route_driving(
    a: LatLng,
    b: LatLng,
    c: LatLng,
) -> dict[str, Any]:
    """
    OSRM public demo server: current → pickup → dropoff.
    Returns dict: distance_m, duration_s, coordinates [[lng,lat],...], legs_miles list of 2 legs.
    """
    coords = f"{a.lng},{a.lat};{b.lng},{b.lat};{c.lng},{c.lat}"
    q = urllib.parse.urlencode({"overview": "full", "geometries": "geojson"})
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}?{q}"
    try:
        data = _get_json(url)
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
    return {
        "distance_miles": meters * 0.000621371,
        "duration_seconds": float(route.get("duration", 0)),
        "coordinates": coordinates,
        "leg_miles": leg_miles,
    }
