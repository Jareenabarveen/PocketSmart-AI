from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from .config import get_settings
from .database import Base, engine
from .routers import auth, pages, planners

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.state.settings = settings
app.state.templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)


@app.get("/health")
def health():
    return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}


@app.get("/session-data")
def session_data():
    return {"service": settings.app_name, "model": settings.gemini_model, "environment": settings.environment}
