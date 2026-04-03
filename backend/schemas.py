from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StationBase(BaseModel):
    name: str
    address: Optional[str] = None
    lat: float
    lng: float
    price_per_kwh: float
    power_kw: Optional[float] = None
    network: Optional[str] = None
    connector_types: Optional[str] = None
    phone: Optional[str] = None
    working_hours: Optional[str] = "24/7"
    is_active: Optional[bool] = True

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True
