import json
import logging
from typing import Any
from PIL import Image
from .catalog import find_items
from ..config import get_settings
from ..schemas import HomeRequest, PartyRequest, RecommendationResponse, RecommendationItem

logger = logging.getLogger(__name__)

HOME_ALLOCATION = {"furniture": 0.45, "lighting": 0.20, "decor": 0.20, "buffer": 0.15}
PARTY_ALLOCATION = {"catering": 0.45, "venue": 0.25, "decoration": 0.20, "entertainment": 0.10}


def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=settings.gemini_api_key)
    except ImportError:
        logger.warning("google-genai is not installed; using fallback recommendations")
        return None


def _clean_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def _call_gemini(prompt: str, image: Image.Image | None = None) -> dict[str, Any] | None:
    client = _client()
    if client is None:
        return None
    settings = get_settings()
    from google.genai import types
    contents: list[Any] = [prompt]
    if image is not None:
        contents.append(image)
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.35,
                max_output_tokens=1800,
                response_mime_type="application/json",
            ),
        )
        return _clean_json(response.text or "{}")
    except Exception as exc:  # graceful fallback is intentional
        logger.exception("Gemini request failed: %s", exc)
        return None


def _items(category: str, budget: float, style: str = "") -> list[RecommendationItem]:
    return [RecommendationItem(title=x.title, category=x.category, platform=x.platform, price=x.price, url=x.url, reason=f"Fits the {style or 'selected'} preference and stays within the planner budget.") for x in find_items(category, budget, style)]


def home_recommendations(req: HomeRequest) -> RecommendationResponse:
    allocation = {k: round(req.budget * v, 2) for k, v in HOME_ALLOCATION.items()}
    prompt = f"""You are PocketSmart AI's home interior budget planner. Return JSON only with keys summary and recommendations.\nBudget INR: {req.budget}. City: {req.city}. Style: {req.style}. Rooms: {req.rooms}. Quantities: {req.items}. Notes: {req.notes}.\nGive practical suggestions, do not invent live prices, and mention that prices/availability must be verified. Recommendations should include title, category, platform, price, url, reason."""
    ai = _call_gemini(prompt)
    if ai and isinstance(ai.get("recommendations"), list):
        recs = [RecommendationItem.model_validate(x) for x in ai["recommendations"] if isinstance(x, dict)]
        return RecommendationResponse(planner="home", budget=req.budget, allocation=allocation, summary=str(ai.get("summary", "AI-generated home plan.")), recommendations=recs, ai_powered=True)
    recs = _items("furniture", allocation["furniture"], req.style) + _items("lighting", allocation["lighting"], req.style) + _items("decor", allocation["decor"], req.style)
    return RecommendationResponse(planner="home", budget=req.budget, allocation=allocation, summary=f"A {req.style} home plan for {', '.join(req.rooms)} with a 15% buffer reserved for delivery or unexpected costs.", recommendations=recs, ai_powered=False, warnings=["Gemini is not configured or did not return usable JSON; showing deterministic catalog fallback recommendations."])


def party_recommendations(req: PartyRequest) -> RecommendationResponse:
    allocation = {k: round(req.budget * v, 2) for k, v in PARTY_ALLOCATION.items()}
    prompt = f"""You are PocketSmart AI's event budget planner. Return JSON only with keys summary and recommendations.\nBudget INR: {req.budget}. City: {req.city}. Event: {req.event_type}. Guests: {req.guests}. Venue: {req.venue}. Date: {req.date}. Notes: {req.notes}.\nSuggest catering, venue, decoration and entertainment. Do not claim live availability or exact current vendor prices. Each recommendation needs title, category, platform, price, url, reason."""
    ai = _call_gemini(prompt)
    if ai and isinstance(ai.get("recommendations"), list):
        recs = [RecommendationItem.model_validate(x) for x in ai["recommendations"] if isinstance(x, dict)]
        return RecommendationResponse(planner="party", budget=req.budget, allocation=allocation, summary=str(ai.get("summary", "AI-generated party plan.")), recommendations=recs, ai_powered=True)
    recs = _items("catering", allocation["catering"], req.event_type) + _items("venue", allocation["venue"], req.event_type) + _items("decoration", allocation["decoration"], req.event_type)
    return RecommendationResponse(planner="party", budget=req.budget, allocation=allocation, summary=f"A {req.event_type} plan for {req.guests} guests, prioritizing food first, then venue and decoration.", recommendations=recs, ai_powered=False, warnings=["Gemini is not configured or did not return usable JSON; showing deterministic catalog fallback recommendations."])


def jewelry_recommendations(budget: float, occasion: str, style: str, outfit_notes: str = "", image: Image.Image | None = None) -> RecommendationResponse:
    allocation = {"jewelry": round(budget * 0.90, 2), "buffer": round(budget * 0.10, 2)}
    prompt = f"""You are PocketSmart AI's jewelry stylist. Return JSON only with keys summary and recommendations.\nBudget INR: {budget}. Occasion: {occasion}. Style: {style}. Outfit notes: {outfit_notes}.\nIf an image is supplied, infer broad color/style cues only; do not identify the person. Recommend jewelry that complements the outfit. Do not claim live prices. Each recommendation needs title, category, platform, price, url, reason."""
    ai = _call_gemini(prompt, image)
    if ai and isinstance(ai.get("recommendations"), list):
        recs = [RecommendationItem.model_validate(x) for x in ai["recommendations"] if isinstance(x, dict)]
        return RecommendationResponse(planner="jewelry", budget=budget, allocation=allocation, summary=str(ai.get("summary", "AI-generated jewelry plan.")), recommendations=recs, ai_powered=True)
    style_key = style or occasion
    recs = _items("jewelry", allocation["jewelry"], style_key)
    return RecommendationResponse(planner="jewelry", budget=budget, allocation=allocation, summary=f"A {style} jewelry shortlist for a {occasion} occasion, with 10% kept as a budget buffer.", recommendations=recs, ai_powered=False, warnings=["Gemini is not configured or did not return usable JSON; showing deterministic catalog fallback recommendations."])
