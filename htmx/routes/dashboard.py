from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from htmx.core import database as db

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/fleet-status")
async def get_fleet_status(request: Request):
    data = db.get_fleet_status()
    # Return HTML partial
    return templates.TemplateResponse("components/stats_grid.html", {"request": request, "stats": data})

@router.get("/map-data")
async def get_map_data(request: Request):
    df = db.get_vessel_position()
    # Rename columns for simpler JS access if needed, or just use as is
    # The DF has columns: "code_vessel", "Nama Kapal", "Status", "latitude", "longitude", "speed", "heading"
    # Mapping to cleaner dict keys
    vessels = []
    if not df.empty:
        for _, row in df.iterrows():
            vessels.append({
                "code_vessel": row["code_vessel"],
                "name": row["Nama Kapal"],
                "reported_status": row["Status"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "speed": row["speed"]
            })
            
    import json
    return templates.TemplateResponse("components/map_view.html", {"request": request, "vessels_json": json.dumps(vessels)})


@router.get("/anomalies")
async def get_anomalies(request: Request):
    df = db.get_operational_anomalies()
    anomalies = df.to_dict('records') if not df.empty else []
    return templates.TemplateResponse("components/anomalies_list.html", {"request": request, "anomalies": anomalies})

@router.get("/financials")
async def get_financials(request: Request):
    metrics = db.get_financial_metrics()
    return templates.TemplateResponse("components/financial_card.html", {"request": request, "metrics": metrics})

@router.get("/environmental")
async def get_environmental(request: Request):
    df = db.get_environmental_compliance_dashboard()
    # Just take the latest day for the summary card
    latest = df.iloc[0].to_dict() if not df.empty else {}
    return templates.TemplateResponse("components/environmental_card.html", {"request": request, "data": latest})
