from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import typer

from .datasets import (
    fetch_hk_flat_tolls,
    fetch_hk_timevarying_tolls,
    fetch_hk_toll_points,
)
from .engine import annotate_geojson_with_tolls, compute_tolls
from .geo import parse_coords_arg

app = typer.Typer(help="hktoll: compute Hong Kong road tolls from official datasets.")


@app.command()
def route(
    coords: Optional[str] = typer.Option(None, help="lon,lat;lon,lat;..."),
    vehicle: str = typer.Option("private_car"),
    when: Optional[str] = typer.Option(
        None, help="ISO8601 local time, e.g. 2025-09-17T08:30:00+08:00"
    ),
    input: Optional[str] = typer.Option(
        None, "--input", "-i", help="GeoJSON LineString file"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Write JSON result here"
    ),
):
    """Compute tolls for a route via coords or a GeoJSON LineString."""
    if coords is None and input is None:
        raise typer.BadParameter("Provide either --coords or --input")
    if coords:
        route_coords = parse_coords_arg(coords)
        route_obj = {"type": "LineString", "coordinates": route_coords}
    else:
        route_obj = json.load(open(input, "r", encoding="utf-8"))
    ts = datetime.fromisoformat(when) if when else None
    events, total = compute_tolls(route_obj, vehicle=vehicle, when=ts)
    out = {"total_hkd": total, "events": [e.model_dump() for e in events]}
    if output:
        json.dump(
            out, open(output, "w", encoding="utf-8"), ensure_ascii=False, indent=2
        )
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2))


@app.command("annotate-geojson")
def annotate_geojson(
    input: str = typer.Argument(..., help="FeatureCollection of LineStrings"),
    output: Optional[str] = typer.Option(None, "--output", "-o"),
    vehicle: str = typer.Option("private_car"),
    when: Optional[str] = typer.Option(None),
):
    fc = json.load(open(input, "r", encoding="utf-8"))
    ts = datetime.fromisoformat(when) if when else None
    annotated = annotate_geojson_with_tolls(fc, vehicle=vehicle, when=ts)
    if output:
        json.dump(
            annotated, open(output, "w", encoding="utf-8"), ensure_ascii=False, indent=2
        )
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(json.dumps(annotated, ensure_ascii=False, indent=2))


@app.command("refresh-data")
def refresh_data():
    fetch_hk_flat_tolls()
    fetch_hk_timevarying_tolls()
    fetch_hk_toll_points()
    typer.echo("Datasets downloaded and cached.")


if __name__ == "__main__":
    app()
