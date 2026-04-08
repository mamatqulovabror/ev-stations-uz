from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    price_per_kwh = Column(Float, nullable=False)
    power_kw = Column(Float)
    network = Column(String)
    connector_types = Column(String)
    phone = Column(String)
    working_hours = Column(String, default="24/7")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
