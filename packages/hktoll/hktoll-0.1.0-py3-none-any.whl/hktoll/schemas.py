from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from pydantic import BaseModel, Field


class TollEvent(BaseModel):
    facility_id: str = Field(..., description="Short code, e.g. CHT/EHC/WHC/TCT/...")
    name: str = Field(..., description="Facility/toll plaza name")
    point: Tuple[float, float] = Field(
        ..., description="[lon, lat] representative point on the route"
    )
    vehicle_class: str = Field(..., description="Normalized vehicle class")
    rate_hkd: float = Field(..., description="Fee in HKD")
    currency: str = "HKD"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source: str = "data.gov.hk"
