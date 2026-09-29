from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import current_user
from ..models import User, RecommendationHistory
from ..security import decode_access_token

router = APIRouter()


def user_optional(request: Request, db: Session):
    token = request.cookies.get("access_token")
    uid = decode_access_token(token) if token else None
    return db.get(User, int(uid)) if uid else None


@router.get("/", name="home")
def home(request: Request, db: Session = Depends(get_db)):
    return request.app.state.templates.TemplateResponse("index.html", {"request": request, "user": user_optional(request, db)})


@router.get("/dashboard")
def dashboard(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(RecommendationHistory).filter_by(user_id=user.id).order_by(RecommendationHistory.created_at.desc()).limit(5).all()
    return request.app.state.templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "history": rows})


@router.get("/home-planner")
def home_planner(request: Request, db: Session = Depends(get_db)):
    user = user_optional(request, db)
    if not user: return RedirectResponse("/login", 303)
    return request.app.state.templates.TemplateResponse("home_planner.html", {"request": request, "user": user})


@router.get("/party-planner")
def party_planner(request: Request, db: Session = Depends(get_db)):
    user = user_optional(request, db)
    if not user: return RedirectResponse("/login", 303)
    return request.app.state.templates.TemplateResponse("party_planner.html", {"request": request, "user": user})


@router.get("/jewelry-planner")
def jewelry_planner(request: Request, db: Session = Depends(get_db)):
    user = user_optional(request, db)
    if not user: return RedirectResponse("/login", 303)
    return request.app.state.templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user})


@router.get("/history-page")
def history_page(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(RecommendationHistory).filter_by(user_id=user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse("history.html", {"request": request, "user": user, "history": rows})
