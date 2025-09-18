from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .engine import compute_tolls
from .schemas import TollEvent

app = FastAPI(title="hktoll", version="0.1.0")


class RouteReq(BaseModel):
    coords: List[Tuple[float, float]] = Field(
        ..., description="List of [lon,lat] pairs"
    )
    vehicle: str = "private_car"
    when: Optional[datetime] = None


class RouteResp(BaseModel):
    total_hkd: float
    events: List[TollEvent]


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/tolls/route", response_model=RouteResp)
def tolls_route(req: RouteReq):
    events, total = compute_tolls(route=req.coords, vehicle=req.vehicle, when=req.when)
    return RouteResp(total_hkd=total, events=events)


def main(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("hktoll.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
