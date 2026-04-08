from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import math
from datetime import datetime, timedelta

from database import get_db, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EV Stations UZ", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# UTIL
# =========================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon2)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def update_station_status(db: Session):
    now = datetime.utcnow()

    stations = db.query(models.Station).all()

    for s in stations:
        if s.last_ping:
            if now - s.last_ping > timedelta(seconds=60):
                s.status = "offline"

    db.commit()

# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "EV Stations UZ API v3",
        "status": "running",
        "features": ["live_status", "sessions", "ping"]
    }

# =========================
# STATIONS
# =========================

@app.get("/api/stations", response_model=List[schemas.Station])
def get_stations(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: Optional[float] = Query(None),
    max_price: float = Query(2000),
    network: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    update_station_status(db)

    query = db.query(models.Station).filter(
        models.Station.price_per_kwh < max_price,
        models.Station.is_active == True
    )

    if network:
        query = query.filter(models.Station.network == network)

    stations = query.limit(100).all()

    if lat and lng and radius:
        stations = [
            s for s in stations
            if haversine(lat, lng, s.lat, s.lon) <= radius
        ]

    return stations


@app.get("/api/stations/{station_id}", response_model=schemas.Station)
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    return station


@app.post("/api/stations", response_model=schemas.Station)
def create_station(station: schemas.StationCreate, db: Session = Depends(get_db)):
    db_station = models.Station(**station.dict())

    db.add(db_station)
    db.commit()
    db.refresh(db_station)

    return db_station

# =========================
# 🔥 REAL-TIME PING
# =========================

@app.post("/api/stations/{station_id}/ping")
def ping_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    station.last_ping = datetime.utcnow()

    # agar busy bo‘lmasa available qilamiz
    if station.status != "busy":
        station.status = "available"

    db.commit()

    return {"status": station.status}

# =========================
# 🔥 CHARGING SESSION (CORE)
# =========================

@app.post("/api/sessions/start")
def start_session(station_id: int, user_id: int, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    if station.status == "busy":
        raise HTTPException(status_code=400, detail="Station already busy")

    session = models.ChargingSession(
        station_id=station_id,
        user_id=user_id,
        start_time=datetime.utcnow()
    )

    station.status = "busy"

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "status": "started"
    }


@app.post("/api/sessions/end")
def end_session(session_id: int, kwh_used: float, db: Session = Depends(get_db)):
    session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.end_time:
        raise HTTPException(status_code=400, detail="Session already ended")

    session.end_time = datetime.utcnow()
    session.kwh_used = kwh_used

    # 🔥 DYNAMIC PRICE
    station = db.query(models.Station).filter(models.Station.id == session.station_id).first()

    price_per_kwh = station.price_per_kwh if station else 0.2
    session.total_price = kwh_used * price_per_kwh

    if station:
        station.status = "available"

    db.commit()

    return {
        "total_price": session.total_price,
        "kwh_used": kwh_used
    }

# =========================
# NETWORKS
# =========================

@app.get("/api/networks")
def get_networks(db: Session = Depends(get_db)):
    networks = db.query(models.Station.network).distinct().all()
    return [n[0] for n in networks if n[0]]

# =========================
# STATS
# =========================

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func

    total = db.query(models.Station).filter(models.Station.price_per_kwh < 2000).count()

    avg_price = db.query(func.avg(models.Station.price_per_kwh)).filter(
        models.Station.price_per_kwh < 2000
    ).scalar()

    return {
        "total_stations": total,
        "avg_price_per_kwh": round(avg_price or 0, 0),
        "version": "v3"
    }
