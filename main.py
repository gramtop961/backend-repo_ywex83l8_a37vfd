import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Plan, Lead

app = FastAPI(title="Teletext ISP API", description="Backend for Телетекст (Невинномысск)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"service": "Teletext ISP API", "city": "Nevinnomyssk"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Seed default tariff plans if not present
@app.post("/seed/plans")
def seed_plans():
    existing = get_documents("plan", {}, limit=1)
    if existing:
        return {"status": "ok", "message": "Plans already exist"}

    default_plans = [
        Plan(name="Старт", speed_mbps=50, price_rub=390, description="Базовый тариф для общения и учебы", featured=False),
        Plan(name="Оптимум", speed_mbps=100, price_rub=590, description="Комфортный интернет для семьи", featured=True),
        Plan(name="Турбо", speed_mbps=300, price_rub=790, description="Высокая скорость для игр и 4K", featured=False),
        Plan(name="Максимум", speed_mbps=500, price_rub=990, description="Для всего и сразу", featured=False),
    ]
    for p in default_plans:
        create_document("plan", p)
    return {"status": "ok", "inserted": len(default_plans)}


# Public endpoints
@app.get("/plans", response_model=List[Plan])
def list_plans():
    docs = get_documents("plan")
    # Map Mongo docs to Plan objects (ignore extra fields)
    return [
        Plan(
            name=d.get("name"),
            speed_mbps=int(d.get("speed_mbps", 0)),
            price_rub=int(d.get("price_rub", 0)),
            description=d.get("description"),
            featured=bool(d.get("featured", False)),
            unlimited=bool(d.get("unlimited", True)),
        )
        for d in docs
    ]


class LeadIn(Lead):
    pass

class LeadOut(BaseModel):
    id: str

@app.post("/lead", response_model=LeadOut)
def create_lead(lead: LeadIn):
    try:
        new_id = create_document("lead", lead)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
