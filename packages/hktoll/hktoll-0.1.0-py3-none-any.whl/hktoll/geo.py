from __future__ import annotations

import math
from typing import List, Tuple

Coord = Tuple[float, float]  # (lon, lat)


def haversine_m(p1: Coord, p2: Coord) -> float:
    # meters using haversine
    lon1, lat1 = p1
    lon2, lat2 = p2
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def closest_point_distance(coords: List[Coord], pt: Coord) -> float:
    # approximate: min distance from pt to any segment in coords
    # sample segments with point-to-segment distance using haversine on vertices
    # for simplicity, we'll check vertices + midpoints
    best = float("inf")
    if not coords:
        return best
    for i in range(len(coords)):
        d = haversine_m(coords[i], pt)
        if d < best:
            best = d
        if i + 1 < len(coords):
            mid = (
                (coords[i][0] + coords[i + 1][0]) / 2,
                (coords[i][1] + coords[i + 1][1]) / 2,
            )
            d2 = haversine_m(mid, pt)
            if d2 < best:
                best = d2
    return best


def parse_coords_arg(arg: str) -> List[Coord]:
    # "lon,lat;lon,lat;..."
    out: List[Coord] = []
    if not arg:
        return out
    for pair in arg.split(";"):
        lon, lat = pair.split(",")
        out.append((float(lon.strip()), float(lat.strip())))
    return out
