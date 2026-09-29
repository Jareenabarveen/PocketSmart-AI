import io
import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from PIL import Image
from ..database import get_db
from ..deps import current_user
from ..models import RecommendationHistory, User
from ..schemas import HomeRequest, PartyRequest
from ..services.recommender import home_recommendations, party_recommendations, jewelry_recommendations

router = APIRouter()


def save_history(db, user, planner, budget, request_obj, response_obj):
    db.add(RecommendationHistory(user_id=user.id, planner=planner, budget=budget, request_json=json.dumps(request_obj, default=str), response_json=response_obj.model_dump_json()))
    db.commit()


@router.post("/generate-home")
def generate_home(payload: HomeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = home_recommendations(payload)
    save_history(db, user, "home", payload.budget, payload.model_dump(), result)
    return result


@router.post("/generate-party")
def generate_party(payload: PartyRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    result = party_recommendations(payload)
    save_history(db, user, "party", payload.budget, payload.model_dump(), result)
    return result


@router.post("/generate-jewelry")
async def generate_jewelry(request: Request, budget: float = Form(...), occasion: str = Form(...), style: str = Form(...), outfit_notes: str = Form(""), outfit_image: UploadFile | None = File(None), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if budget <= 0 or budget > 10_000_000:
        raise HTTPException(422, "Budget must be between 1 and 10,000,000")
    image = None
    if outfit_image and outfit_image.filename:
        if not outfit_image.content_type or not outfit_image.content_type.startswith("image/"):
            raise HTTPException(400, "Outfit upload must be an image")
        raw = await outfit_image.read()
        if len(raw) > request.app.state.settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, "Image is too large")
        try:
            image = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as exc:
            raise HTTPException(400, "Invalid image file") from exc
    result = jewelry_recommendations(budget, occasion, style, outfit_notes, image)
    save_history(db, user, "jewelry", budget, {"budget": budget, "occasion": occasion, "style": style, "outfit_notes": outfit_notes, "image": bool(image)}, result)
    return result


@router.get("/recommendations-details/{history_id}")
def recommendation_details(history_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(RecommendationHistory, history_id)
    if not item or item.user_id != user.id:
        raise HTTPException(404, "Recommendation not found")
    return json.loads(item.response_json)


@router.get("/history")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(RecommendationHistory).filter_by(user_id=user.id).order_by(RecommendationHistory.created_at.desc()).limit(50).all()
    return [{"id": r.id, "planner": r.planner, "budget": r.budget, "created_at": r.created_at.isoformat(), "request": json.loads(r.request_json)} for r in rows]
