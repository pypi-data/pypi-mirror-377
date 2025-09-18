from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd
import platformdirs

RES_DIR = Path(__file__).resolve().parent / "resources"
URLS = json.loads((RES_DIR / "urls.json").read_text())


def cache_dir() -> Path:
    d = Path(os.environ.get("HKTOLL_CACHE_DIR", platformdirs.user_cache_dir("hktoll")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download(url: str) -> bytes:
    # Allow overriding URLs with env vars
    override = os.environ.get("HKTOLL_URL_OVERRIDE_" + re.sub(r"\W+", "_", url).upper())
    if override:
        url = override
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.content


def _download_to_cache(url: str, fname: Optional[str] = None) -> Path:
    data = _download(url)
    if not fname:
        fname = url.rsplit("/", 1)[-1]
    out = cache_dir() / fname
    out.write_bytes(data)
    return out


def fetch_hk_flat_tolls() -> pd.DataFrame:
    path = _download_to_cache(URLS["hk_flat_toll_csv"])
    df = pd.read_csv(path)
    return _normalize_columns(df)


def fetch_hk_timevarying_tolls() -> pd.DataFrame:
    path = _download_to_cache(URLS["hk_timevarying_toll_csv"])
    df = pd.read_csv(path)
    return _normalize_columns(df)


def fetch_hk_toll_points() -> List[Dict[str, Any]]:
    # Returns a list of {name, lon, lat}
    path = _download_to_cache(URLS["hk_traffic_features_kmz"])
    with zipfile.ZipFile(path, "r") as zf:
        # Typically 'doc.kml' inside a KMZ
        with zf.open("doc.kml") as f:
            kml = f.read()
    # Parse KML
    root = ET.fromstring(kml)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    points: List[Dict[str, Any]] = []
    for pm in root.findall(".//kml:Placemark", ns):
        name_el = pm.find("kml:name", ns)
        name = name_el.text.strip() if name_el is not None and name_el.text else ""
        # Only keep toll plaza placemarks (name filter, conservative)
        if not re.search(r"toll\s*plaza", name, re.IGNORECASE):
            continue
        pt = pm.find(".//kml:Point/kml:coordinates", ns)
        if pt is None or not pt.text:
            continue
        lon, lat, *_ = [float(x) for x in pt.text.strip().split(",")]
        points.append({"name": name, "lon": lon, "lat": lat})
    return points


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(s: str) -> str:
        s = re.sub(r"[^0-9A-Za-z]+", "_", s.strip().lower())
        s = re.sub(r"_+", "_", s).strip("_")
        return s

    df = df.copy()
    df.columns = [norm(c) for c in df.columns]
    return df
