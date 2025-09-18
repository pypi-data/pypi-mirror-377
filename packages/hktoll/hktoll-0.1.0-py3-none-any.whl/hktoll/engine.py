from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .adapters.hk import match_and_price
from .schemas import TollEvent


def compute_tolls(
    route: List[Tuple[float, float]] | Dict[str, Any],
    vehicle: str = "private_car",
    when: Optional[datetime] = None,
) -> tuple[list[TollEvent], float]:
    """Given a route (list of (lon,lat) OR a GeoJSON LineString/Feature), return events + total."""
    coords: List[Tuple[float, float]]
    if isinstance(route, dict):
        # GeoJSON LineString or Feature
        if route.get("type") == "Feature":
            geom = route.get("geometry") or {}
        else:
            geom = route
        if geom.get("type") != "LineString":
            raise ValueError("GeoJSON must be a LineString or Feature(LineString)")
        coords = [(float(x), float(y)) for (x, y) in geom.get("coordinates", [])]
    else:
        coords = [(float(x), float(y)) for (x, y) in route]
    events = match_and_price(coords, vehicle=vehicle, when=when)
    total = sum(e.rate_hkd for e in events)
    return events, float(round(total, 2))


def annotate_geojson_with_tolls(
    fc: Dict[str, Any], vehicle: str = "private_car", when: Optional[datetime] = None
) -> Dict[str, Any]:
    if not isinstance(fc, dict) or fc.get("type") != "FeatureCollection":
        raise ValueError("Expected a GeoJSON FeatureCollection")
    total = 0.0
    for feat in fc.get("features", []):
        geom = feat.get("geometry") or {}
        if geom.get("type") != "LineString":
            continue
        events, subtotal = compute_tolls(geom, vehicle=vehicle, when=when)
        props = feat.setdefault("properties", {})
        props["toll_hkd"] = subtotal
        props["toll_events"] = [e.model_dump() for e in events]
        total += subtotal
    meta = fc.setdefault("meta", {})
    meta["toll_hkd_total"] = float(round(total, 2))
    return fc
