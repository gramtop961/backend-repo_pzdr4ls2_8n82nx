from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db, create_document, get_documents
from datetime import datetime

app = FastAPI(title="BodyScan.pl API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class Booking(BaseModel):
    location_id: str = Field(..., description="Club/location identifier")
    full_name: str
    email: str
    phone: Optional[str] = None
    date: str = Field(..., description="ISO date string, e.g., 2025-01-20")
    time: str = Field(..., description="HH:mm time")
    test_package: str = Field(..., description="InBody | Performance x4 | Full + AI Report")

class Location(BaseModel):
    name: str
    lat: float
    lng: float
    address: str
    city: str
    club_brand: Optional[str] = None

@app.get("/test")
def test():
    try:
        ok = db is not None
        return {"ok": ok}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/locations", response_model=List[Location])
def list_locations():
    # Demo dataset (these could be stored in DB; read-only for MVP)
    sample = [
        {"name": "BodyScan @ CityFit Rondo ONZ", "lat": 52.233, "lng": 20.999, "address": "al. Jana Pawła II 18", "city": "Warszawa", "club_brand": "CityFit"},
        {"name": "BodyScan @ Zdrofit Ursynów", "lat": 52.154, "lng": 21.045, "address": "ul. KEN 36", "city": "Warszawa", "club_brand": "Zdrofit"},
        {"name": "BodyScan @ Pure Jatomi Gdańsk", "lat": 54.352, "lng": 18.646, "address": "ul. Długa 10", "city": "Gdańsk", "club_brand": "Jatomi"}
    ]
    return sample

@app.post("/book")
def create_booking(booking: Booking):
    try:
        doc_id = create_document("booking", booking)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings")
def get_bookings(location_id: Optional[str] = None, limit: int = 100):
    try:
        filter_q = {"location_id": location_id} if location_id else {}
        docs = get_documents("booking", filter_q, limit)
        # Convert ObjectId
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
