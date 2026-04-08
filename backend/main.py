from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import math
from database import get_db, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EV Stations UZ", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

@app.get("/")
def root():
    return {"message": "EV Stations UZ API", "filter": "price < 2000 som/kWh"}


# =========================
# USERS
# =========================

@app.post("/api/users/login")
def user_login(telegram_id: int, first_name: str = "", last_name: str = "", username: str = "", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if not user:
        user = models.User(telegram_id=telegram_id, first_name=first_name, last_name=last_name, username=username, balance=0)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.first_name = first_name
        user.last_name = last_name
        db.commit()
    return {"id": user.id, "telegram_id": user.telegram_id, "first_name": user.first_name, "last_name": user.last_name, "username": user.username, "balance": user.balance}

@app.get("/api/users/{telegram_id}")
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "telegram_id": user.telegram_id, "first_name": user.first_name, "balance": user.balance}


@app.get("/api/stations", response_model=List[schemas.Station])
def get_stations(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: Optional[float] = Query(None, description="km"),
    max_price: float = Query(2000, description="max price per kWh in som"),
    network: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Station).filter(
        models.Station.price_per_kwh < max_price,
        models.Station.is_active == True
    )
    if network:
        query = query.filter(models.Station.network == network)
    stations = query.all()
    if lat and lng and radius:
        stations = [s for s in stations if haversine(lat, lng, s.lat, s.lng) <= radius]
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

@app.get("/api/networks")
def get_networks(db: Session = Depends(get_db)):
    networks = db.query(models.Station.network).distinct().all()
    return [n[0] for n in networks if n[0]]

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Station).filter(models.Station.price_per_kwh < 2000).count()
    from sqlalchemy import func
    avg_price = db.query(func.avg(models.Station.price_per_kwh)).filter(
        models.Station.price_per_kwh < 2000
    ).scalar()
    return {
        "total_stations": total,
        "avg_price_per_kwh": round(avg_price or 0, 0),
        "filter": "price < 2000 som/kWh"
    }
