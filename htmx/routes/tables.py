from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from htmx.core import database as db

router = APIRouter()
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/logs", response_class=templates.TemplateResponse)
async def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@router.get("/api/tables/logs")
async def get_logs_table(request: Request):
    df = db.get_logs()
    logs = df.to_dict('records') if not df.empty else []
    return templates.TemplateResponse("components/logs_table.html", {"request": request, "logs": logs})

@router.get("/api/tables/clients")
async def get_clients_table(request: Request):
    df = db.get_client_reliability_scoring()
    clients = df.to_dict('records') if not df.empty else []
    return templates.TemplateResponse("components/clients_table.html", {"request": request, "clients": clients})
