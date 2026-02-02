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

@router.get("/api/analytics/insights")
async def get_analytics_insights(request: Request):
    financials = db.get_financial_metrics()
    orders = db.get_order_stats()
    
    # Calculate derived metrics
    total_rev = financials.get('total_revenue', 0)
    completed = orders.get('completed', 0)
    total_orders = orders.get('total_orders', 1) # avoid div by zero
    
    rev_per_order = total_rev / completed if completed > 0 else 0
    completion_rate = (completed / total_orders) * 100 if total_orders > 0 else 0
    
    metrics = {
        "revenue_per_order": rev_per_order,
        "completion_rate": completion_rate,
        "completed_orders": completed,
        "total_orders": total_orders,
        "total_revenue": total_rev
    }
    
    return templates.TemplateResponse("components/analytics_insights.html", {"request": request, "metrics": metrics})
