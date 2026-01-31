from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from htmx.core import database as db

router = APIRouter()
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    # Security check: Ensure user is Admin (should be handled by middleware + strict check here)
    user_role = request.cookies.get("session_role")
    if user_role != "Admin":
         return HTMLResponse("<h1>Access Denied</h1><p>You need Admin privileges.</p>", status_code=403)
         
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/api/admin/users")
async def get_users_table(request: Request):
    df = db.get_all_users()
    users = df.to_dict('records') if not df.empty else []
    return templates.TemplateResponse("components/users_table.html", {"request": request, "users": users})

@router.post("/api/admin/users")
async def create_user(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    success, msg = db.create_new_user(username, password, role)
    if not success:
        return JSONResponse(status_code=400, content={"message": msg})
    return JSONResponse(content={"message": "ok"})

@router.delete("/api/admin/users/{username}")
async def delete_user_endpoint(username: str):
    if username == "admin":
        return JSONResponse(status_code=400, content={"message": "Cannot delete root admin"})
        
    success = db.delete_user(username)
    if not success:
        return JSONResponse(status_code=500, content={"message": "Failed to delete"})
    return JSONResponse(content={"message": "ok"})
