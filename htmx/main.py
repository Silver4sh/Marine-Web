from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
import os
import uvicorn

app = FastAPI(title="MarineOS Dashboard", version="2.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="htmx/static"), name="static")

# Templates
templates = Jinja2Templates(directory="htmx/templates")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("htmx/static/favicon.ico")

from htmx.routes import dashboard, analytics, tables, auth, environment, admin
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(tables.router)
app.include_router(environment.router)
app.include_router(admin.router)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Allow static files and login page
    if request.url.path.startswith("/static") or request.url.path in ["/login", "/favicon.ico"]:
        response = await call_next(request)
        return response
    
    # Check session cookie
    user = request.cookies.get("session_user")
    if not user:
        return RedirectResponse(url="/login")
        
    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
