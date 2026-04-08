from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# =========================
# STATIONS
# =========================
class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    address = Column(String)

    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)  # 🔥 FIX (lng → lon)

    price_per_kwh = Column(Float, nullable=False, index=True)
    power_kw = Column(Float)

    network = Column(String)
    connector_types = Column(String)

    phone = Column(String)
    working_hours = Column(String, default="24/7")

    is_active = Column(Boolean, default=True)

    # 🔥 REAL-TIME STATUS
    status = Column(String, default="offline")  # available / busy / offline
    last_ping = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATION
    sessions = relationship("ChargingSession", back_populates="station")


# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 RELATION
    sessions = relationship("ChargingSession", back_populates="user")


# =========================
# CHARGING SESSIONS
# =========================
class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    station_id = Column(Integer, ForeignKey("stations.id"))

    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    kwh_used = Column(Float, default=0)
    total_price = Column(Float, default=0)

    status = Column(String, default="active")  # active / completed

    # 🔥 RELATION
    user = relationship("User", back_populates="sessions")
    station = relationship("Station", back_populates="sessions")


# =========================
# FAVORITES
# =========================
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    station_id = Column(Integer, ForeignKey("stations.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
