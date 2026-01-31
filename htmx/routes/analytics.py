from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from htmx.core import database as db
import json

router = APIRouter()
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/analytics", response_class=templates.TemplateResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@router.get("/api/charts/revenue")
async def get_revenue_chart(request: Request):
    df = db.get_revenue_analysis()
    # Prepare data for Chart.js
    labels = []
    data = []
    if not df.empty:
        # Convert Timestamp to string
        labels = [d.strftime('%Y-%m') for d in df['month']]
        data = df['revenue'].tolist()
    
    chart_config = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Monthly Revenue",
                "data": data,
                "backgroundColor": "rgba(14, 165, 233, 0.8)",
                "borderRadius": 4
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {"legend": {"display": False}}
        }
    }
    
    return templates.TemplateResponse("components/chart_canvas.html", {
        "request": request, 
        "chart_id": "revenueChart", 
        "chart_config": json.dumps(chart_config),
        "title": "Revenue Trend"
    })

@router.get("/api/charts/utilization")
async def get_utilization_chart(request: Request):
    df = db.get_vessel_utilization_stats()
    labels = []
    data = []
    if not df.empty:
        labels = df['vessel_name'].tolist()
        data = df['utilization_rate'].tolist()

    chart_config = {
        "type": "doughnut",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": [
                    "#0ea5e9", "#22c55e", "#f97316", "#ef4444", "#8b5cf6"
                ]
            }]
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False
        }
    }

    return templates.TemplateResponse("components/chart_canvas.html", {
        "request": request, 
        "chart_id": "utilizationChart", 
        "chart_config": json.dumps(chart_config),
        "title": "Fleet Utilization"
    })
