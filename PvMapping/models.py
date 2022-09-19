from __future__ import annotations

import dataclasses
from typing import Optional

import numpy as np


@dataclasses.dataclass
class Plant:
    id_: int
    xtf_id: int
    lat: float
    lon: float
    installed_capacity_kw: float
    slope_deg: float
    orientation_deg: float
    municipality: str
    address: str
    zipcode: int
    canton: str

    nearest_meter_id: Optional[int]


@dataclasses.dataclass
class Meter:
    id_: int
    utility: str
    lat: float
    lon: float
    installed_capacity_kw: float
    slope_deg: float
    orientation_deg: float
    municipality: str
    address: str


@dataclasses.dataclass
class RealTime:
    timestamp: np.timestamp64
    plant_id: int
    power_kw: float
