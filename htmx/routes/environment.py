from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from htmx.core import database as db
import pandas as pd
import json

router = APIRouter()
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/environment", response_class=templates.TemplateResponse)
async def environment_page(request: Request):
    return templates.TemplateResponse("environment.html", {"request": request})

@router.get("/api/environment/buoys")
async def get_buoy_fleet(request: Request):
    df = db.get_buoy_fleet()
    buoys = df.to_dict('records') if not df.empty else []
    # Format dates
    for b in buoys:
        if pd.notnull(b.get('last_update')):
            b['last_update_fmt'] = b['last_update'].strftime("%d %b %H:%M")
        else:
            b['last_update_fmt'] = "-"
            
    return templates.TemplateResponse("components/buoy_grid.html", {"request": request, "buoys": buoys})

@router.get("/api/environment/heatmap-data")
async def get_heatmap_data(request: Request):
    df = db.get_data_water()
    data_points = []
    if not df.empty:
        # Just return raw data for frontend JS to handle
        # Columns: latitude, longitude, salinitas, etc.
        data_points = df.fillna(0).to_dict('records')
        # Convert timestamp to str
        for d in data_points:
            d['latest_timestamp'] = d['latest_timestamp'].isoformat() if d.get('latest_timestamp') else ""

    return {"data": data_points}

@router.get("/api/environment/buoys/{buoy_id}")
async def get_buoy_detail(request: Request, buoy_id: str):
    df = db.get_buoy_history(buoy_id)
    history = []
    if not df.empty:
        # Convert timestamp for Chart.js
        df['created_at'] = df['created_at'].astype(str)
        history = df.to_dict('records')
    
    return templates.TemplateResponse("components/buoy_detail.html", {
        "request": request, 
        "buoy_id": buoy_id,
        "history": json.dumps(history), # Pass as JSON string for JS
        "history_raw": history 
    })

@router.get("/api/environment/insights")
async def get_environment_insights(request: Request):
    # Reuse existing queries for efficiency
    compliance = db.get_environmental_compliance_dashboard()
    buoy_fleet = db.get_buoy_fleet()
    
    # Calculate metrics
    latest_compliance = compliance.iloc[0].to_dict() if not compliance.empty else {}
    
    total_buoys = len(buoy_fleet)
    active_buoys = len(buoy_fleet[buoy_fleet['status'] == 'Active']) if not buoy_fleet.empty else 0
    
    metrics = {
        "avg_turbidity": latest_compliance.get('avg_turbidity', 0),
        "high_turbidity_events": latest_compliance.get('high_turbidity_events', 0),
        "active_buoys": active_buoys,
        "total_buoys": total_buoys
    }
    
    return templates.TemplateResponse("components/environment_insights.html", {"request": request, "metrics": metrics})
