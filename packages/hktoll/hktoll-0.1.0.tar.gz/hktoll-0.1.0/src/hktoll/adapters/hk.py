from __future__ import annotations

import difflib
import re
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd

from ..datasets import (
    fetch_hk_flat_tolls,
    fetch_hk_timevarying_tolls,
    fetch_hk_toll_points,
)
from ..geo import closest_point_distance
from ..schemas import TollEvent

# Simple alias map (can be extended)
ALIASES = {
    "western harbour crossing": ("WHC", ["whc", "western harbour crossing"]),
    "eastern harbour crossing": ("EHC", ["ehc", "eastern harbour crossing"]),
    "cross-harbour tunnel": ("CHT", ["cht", "cross-harbour tunnel"]),
    "tate's cairn tunnel": (
        "TCT",
        ["tct", "tates cairn tunnel", "tate's cairn tunnel"],
    ),
    "lion rock tunnel": ("LRT", ["lrt", "lion rock tunnel"]),
    "aberdeen tunnel": ("ABT", ["abt", "aberdeen tunnel"]),
    "shing mun tunnels": ("SMT", ["smt", "shing mun tunnels"]),
    "tai lam tunnel": ("TLT", ["tlt", "tai lam tunnel"]),
}


def _normalize_name(n: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", n.strip().lower()).strip()


def _facility_id_from_name(name: str) -> str:
    n = _normalize_name(name)
    best = None
    for key, (code, aliases) in ALIASES.items():
        for a in [key] + aliases:
            if _normalize_name(a) in n:
                return code
            # fuzzy fallback
            if difflib.SequenceMatcher(None, _normalize_name(a), n).ratio() > 0.85:
                best = code
    return best or n[:8].upper()


def match_and_price(
    coords: List[Tuple[float, float]], vehicle: str, when: Optional[datetime]
) -> List[TollEvent]:
    # Use nearest toll plaza points as a proxy for facility usage
    points = fetch_hk_toll_points()
    hits = []
    for p in points:
        d = closest_point_distance(coords, (p["lon"], p["lat"]))
        if d <= 120:  # meters threshold
            hits.append(p)

    # Deduplicate by facility (name root)
    seen = {}
    for p in hits:
        fid = _facility_id_from_name(p["name"])
        if fid not in seen:
            seen[fid] = p

    flat = fetch_hk_flat_tolls()
    tv = fetch_hk_timevarying_tolls()

    events: List[TollEvent] = []
    for fid, p in seen.items():
        amount, vfrom, vto, fname = _lookup_amount(
            fid, p["name"], vehicle, when, flat, tv
        )
        events.append(
            TollEvent(
                facility_id=fid,
                name=fname or p["name"],
                point=(p["lon"], p["lat"]),
                vehicle_class=vehicle,
                rate_hkd=float(amount or 0.0),
                valid_from=vfrom,
                valid_to=vto,
            )
        )
    return events


def _lookup_amount(
    fid: str,
    name: str,
    vehicle: str,
    when: Optional[datetime],
    flat: pd.DataFrame,
    tv: pd.DataFrame,
):
    # Normalize columns and attempt to match by name and vehicle
    vehicle_norm = vehicle.strip().lower()

    def col(df, *cands, default=None):
        for c in cands:
            if c in df.columns:
                return c
        return default

    # Try time-varying first if timestamp provided
    if when is not None and not tv.empty:
        cname = col(tv, "facility", "facility_name", "facility_en", "facility_name_en")
        vcol = col(tv, "vehicle_class", "vehicle")
        scol = col(tv, "start_time", "start", "from_time")
        ecol = col(tv, "end_time", "end", "to_time")
        amtcol = col(tv, "toll_hkd", "amount", "toll", "price")

        if cname and vcol and scol and ecol and amtcol:
            # candidate rows by fuzzy name match
            tv["__name_norm"] = tv[cname].astype(str).str.lower()
            cand = tv[
                tv["__name_norm"].str.contains(
                    _normalize_name(name).split()[0], na=False
                )
            ]
            if cand.empty:
                # fallback: find alias by code
                cand = tv[
                    tv[cname]
                    .astype(str)
                    .str.lower()
                    .str.contains(fid.lower(), na=False)
                ]
            # match vehicle
            if not cand.empty:
                vc = cand[vcol].astype(str).str.lower()
                cand = cand[vc.str.contains(vehicle_norm, na=False)]
            if not cand.empty:
                # parse times as HH:MM
                hhmm = when.strftime("%H:%M")

                def within(row):
                    st = str(row[scol])[:5]
                    et = str(row[ecol])[:5]
                    return st <= hhmm < et if st < et else (hhmm >= st or hhmm < et)

                cand2 = cand[cand.apply(within, axis=1)]
                if not cand2.empty:
                    row = cand2.iloc[0]
                    tryname = str(row[cname])
                    amount = float(row[amtcol])
                    # valid window (best-effort: same day)
                    vfrom = when.replace(
                        hour=int(str(row[scol])[:2]),
                        minute=int(str(row[scol])[3:5]),
                        second=0,
                        microsecond=0,
                    )
                    vto = when.replace(
                        hour=int(str(row[ecol])[:2]),
                        minute=int(str(row[ecol])[3:5]),
                        second=0,
                        microsecond=0,
                    )
                    return amount, vfrom, vto, tryname

    # Fallback to flat
    if not flat.empty:
        cname = col(
            flat, "facility", "facility_name", "facility_en", "facility_name_en"
        )
        vcol = col(flat, "vehicle_class", "vehicle")
        amtcol = col(flat, "toll_hkd", "amount", "toll", "price")
        if cname and vcol and amtcol:
            flat["__name_norm"] = flat[cname].astype(str).str.lower()
            cand = flat[
                flat["__name_norm"].str.contains(
                    _normalize_name(name).split()[0], na=False
                )
            ]
            if cand.empty:
                cand = flat[
                    flat[cname]
                    .astype(str)
                    .str.lower()
                    .str.contains(fid.lower(), na=False)
                ]
            if not cand.empty:
                vc = cand[vcol].astype(str).str.lower()
                cand = cand[vc.str.contains(vehicle_norm, na=False)]
            if not cand.empty:
                row = cand.iloc[0]
                tryname = str(row[cname])
                amount = float(row[amtcol])
                return amount, None, None, tryname

    return 0.0, None, None, name
