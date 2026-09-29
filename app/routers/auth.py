from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import current_user
from ..models import User
from ..security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.get("/register")
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request, "user": None})


@router.post("/register")
def register(full_name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    email = email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        return RedirectResponse("/login?error=Account%20already%20exists", status_code=303)
    user = User(full_name=full_name.strip(), email=email, password_hash=hash_password(password))
    db.add(user); db.commit(); db.refresh(user)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", create_access_token(str(user.id)), httponly=True, samesite="lax", secure=False, max_age=3600)
    return response


@router.get("/login")
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "user": None, "error": request.query_params.get("error")})


@router.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse("/login?error=Invalid%20email%20or%20password", status_code=303)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("access_token", create_access_token(str(user.id)), httponly=True, samesite="lax", secure=False, max_age=3600)
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.post("/token")
def token(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}


@router.get("/session-info")
def session_info(user: User = Depends(current_user)):
    return {"authenticated": True, "user_id": user.id, "email": user.email, "full_name": user.full_name}
