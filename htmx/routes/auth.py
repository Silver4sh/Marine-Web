from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from htmx.core import database as db
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="htmx/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_submit(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    user = db.verify_user(username, password)
    
    if user:
        # Create Session
        session_id = str(uuid.uuid4())
        # In a real app, store session_id in Redis/DB with user data. 
        # Here we will just set a signed cookie for simplicity or use a global dict (not production safe for scalabiltiy but fine for single instance)
        # For better statelessness, let's just set the user info in a secure HTTPOnly cookie
        
        resp = RedirectResponse(url="/", status_code=303)
        resp.set_cookie(key="session_user", value=username, httponly=True)
        resp.set_cookie(key="session_role", value=user['role'], httponly=True)
        return resp
    else:
        # Return the form with error
        return HTMLResponse(
            """
            <div class="text-red-500 text-sm mb-4 bg-red-50 p-3 rounded text-center">
                Invalid username or password
            </div>
            """, 
            status_code=401
        )

@router.get("/logout")
async def logout(request: Request):
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_user")
    resp.delete_cookie("session_role")
    return resp
