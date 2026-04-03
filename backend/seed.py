"""Run once to seed sample stations into the database"""
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

STATIONS = [
    {"name": "Tok Bor - Yunusobod", "address": "Yunusobod tumani, Toshkent", "lat": 41.3425, "lng": 69.3158, "price_per_kwh": 1500, "power_kw": 80, "network": "Tok Bor", "connector_types": "CCS2,CHAdeMO", "working_hours": "24/7"},
    {"name": "Tok Bor - Samarqand Darvoza", "address": "Samarqand Darvoza, Toshkent", "lat": 41.2780, "lng": 69.2690, "price_per_kwh": 1400, "power_kw": 120, "network": "Tok Bor", "connector_types": "CCS2,CHAdeMO,Type2", "working_hours": "24/7"},
    {"name": "Tok Bor - Ohangaron", "address": "Ohangaron shahri", "lat": 41.0133, "lng": 69.6517, "price_per_kwh": 1300, "power_kw": 120, "network": "Tok Bor", "connector_types": "CCS2,CHAdeMO", "working_hours": "24/7"},
    {"name": "Beon - Chilonzor", "address": "Chilonzor tumani, Toshkent", "lat": 41.2995, "lng": 69.2401, "price_per_kwh": 1800, "power_kw": 50, "network": "Beon", "connector_types": "Type2,CCS2", "working_hours": "08:00-22:00"},
    {"name": "Beon - Sergeli", "address": "Sergeli tumani, Toshkent", "lat": 41.2340, "lng": 69.2120, "price_per_kwh": 1900, "power_kw": 40, "network": "Beon", "connector_types": "Type2", "working_hours": "09:00-21:00"},
    {"name": "EcoTok - Mirzo Ulugbek", "address": "Mirzo Ulugbek tumani, Toshkent", "lat": 41.3208, "lng": 69.3567, "price_per_kwh": 1600, "power_kw": 60, "network": "EcoTok", "connector_types": "CCS2", "working_hours": "24/7"},
    {"name": "EcoTok - Uchtepa", "address": "Uchtepa tumani, Toshkent", "lat": 41.3050, "lng": 69.2180, "price_per_kwh": 1700, "power_kw": 50, "network": "EcoTok", "connector_types": "CCS2,Type2", "working_hours": "24/7"},
    {"name": "Tok Bor - Namangan", "address": "Namangan shahri", "lat": 41.0011, "lng": 71.6725, "price_per_kwh": 1200, "power_kw": 80, "network": "Tok Bor", "connector_types": "CCS2,CHAdeMO", "working_hours": "24/7"},
    {"name": "Tok Bor - Samarqand", "address": "Samarqand shahri", "lat": 39.6547, "lng": 66.9758, "price_per_kwh": 1350, "power_kw": 100, "network": "Tok Bor", "connector_types": "CCS2,CHAdeMO", "working_hours": "24/7"},
    {"name": "Beon - Andijon", "address": "Andijon shahri", "lat": 40.7821, "lng": 72.3442, "price_per_kwh": 1800, "power_kw": 40, "network": "Beon", "connector_types": "Type2,CCS2", "working_hours": "09:00-22:00"},
]

db = SessionLocal()
added = 0
for s in STATIONS:
    existing = db.query(models.Station).filter(models.Station.name == s["name"]).first()
    if not existing:
        db.add(models.Station(**s))
        added += 1
db.commit()
db.close()
print(f"Seeded {added} new stations (total: {len(STATIONS)})")
