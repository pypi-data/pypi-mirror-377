# hktoll

Compute Hong Kong road **tolls** from **official Transport Department datasets**.
- Input: a route polyline (list of lon/lat pairs) or a GeoJSON LineString/FeatureCollection
- Output: ordered **toll events** (facility, time band, amount) and totals, with HKD currency

## Quick start

```bash
# Create & activate a virtualenv (Linux/macOS)
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -U pip
pip install hktoll  # after publishing to PyPI
# or for local dev:
pip install -e ".[dev]"
```

### CLI

```bash
# Route via coordinates (lon,lat;lon,lat;...)
hktoll route --coords "114.1582,22.2799;114.1640,22.2801;114.1721,22.2975" \                 --vehicle private_car \                 --when "2025-09-17T08:30:00+08:00" -o out.json

# Annotate a GeoJSON FeatureCollection of LineStrings in-place
hktoll annotate-geojson examples/sample_route.geojson -o annotated.geojson
```

### Python API

```python
from datetime import datetime
from hktoll import compute_tolls, annotate_geojson_with_tolls, TollEvent

route = [(114.1582,22.2799),(114.1640,22.2801),(114.1721,22.2975)]
events, total = compute_tolls(route, vehicle="private_car", when=datetime.now())
print(total, [e.dict() for e in events])
```

### REST API (language‑agnostic)

```bash
# Start the server
hktoll serve --host 0.0.0.0 --port 8000
# Call it
curl -X POST http://localhost:8000/v1/tolls/route -H "content-type: application/json" -d '{
  "coords": [[114.1582,22.2799],[114.1640,22.2801],[114.1721,22.2975]],
  "vehicle": "private_car",
  "when": "2025-09-17T08:30:00+08:00"
}'
```

## Data sources (official)

- **Toll rates of tunnel and bridge (flat):** `TUN_BRIDGE_TOLL.csv` (Transport Department, Road Network v2). 
- **Toll rates of tunnel and bridge (time‑varying):** `TUN_BRIDGE_TV_TOLL.csv`.
- **Zebra crossing, yellow box, **toll plaza** and cul‑de‑sac:** `TRAFFIC_FEATURES.kmz` (KML).

The library downloads and caches these files automatically. For details and the latest URLs, see
`src/hktoll/resources/urls.json` and the docs in `docs/GETTING_STARTED.md`.

> Data are provided under DATA.GOV.HK Terms and Conditions; please attribute the source. See
> README footer and `LICENSE` for details.

## Adapter architecture

The code is structured so additional regions can be supported later via adapters (e.g. Singapore ERP, Norway AutoPASS, Dubai Salik).

```text
hktoll/
 ├─ adapters/hk.py     # Hong Kong adapter (default)
 ├─ datasets.py        # download/cache & normalize datasets
 ├─ engine.py          # route -> toll events
 ├─ geo.py             # small geospatial helpers
 ├─ schemas.py         # pydantic models for TollEvent
 ├─ cli.py             # Typer CLI
 └─ server.py          # FastAPI server
```

## Attribution & terms

- Data © Transport Department, HKSAR Government; sourced via DATA.GOV.HK.
- Reuse is allowed for commercial and non‑commercial purposes **subject to** the
  [DATA.GOV.HK Terms and Conditions](https://data.gov.hk/en/terms-and-conditions).
- This library is not affiliated with the Government.

---

See `docs/PUBLISHING.md` for step‑by‑step instructions to:
1) publish on GitHub; 2) distribute on PyPI; 3) run as a language‑agnostic HTTP service.
