import strawberry
from typing import List, Optional
from datetime import datetime, timezone


@strawberry.type
class SolarSite:
    site_id: str
    name: str
    location: str
    capacity: float
    created_at: str


@strawberry.type
class EnergyReading:
    site_id: str
    timestamp: str
    output_kw: float


@strawberry.input
class CreateSiteInput:
    name: str
    location: str
    capacity: float


@strawberry.input
class AddReadingInput:
    site_id: str
    output_kw: float