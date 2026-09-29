# PocketSmart AI

A complete FastAPI + Jinja2 + SQLite + Gemini application based on the supplied PocketSmart AI project documentation.

## Features
- Home Interior budget planner
- Party budget planner
- Jewelry planner with optional outfit image analysis
- Gemini multimodal integration through the official `google-genai` SDK
- Configurable Gemini model via `.env`
- Deterministic fallback recommendations when Gemini is not configured or fails
- SQLite user registration/login and recommendation history
- JWT `/token` endpoint and browser session cookie
- Responsive HTML/CSS/JS frontend
- Mock catalog adapters for Amazon, IKEA, Flipkart, Swiggy, Zomato and OYO-style results
- Automated API tests

## Project structure

```text
pocketsmart_ai/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # environment configuration
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models.py               # User + recommendation history models
│   ├── schemas.py              # Pydantic API models
│   ├── security.py             # password hashing + JWT
│   ├── deps.py                 # authenticated-user dependency
│   ├── routers/
│   │   ├── auth.py             # register/login/logout/token/session
│   │   ├── pages.py             # Jinja page routes
│   │   └── planners.py          # planner APIs
│   ├── services/
│   │   ├── catalog.py           # mock/provider adapter catalog
│   │   └── recommender.py       # Gemini + fallback recommendation engine
│   ├── templates/               # Jinja pages
│   └── static/                  # CSS + browser JavaScript
├── tests/test_app.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## VS Code setup

### 1. Install prerequisites
- Python 3.11+ (3.12 recommended)
- VS Code
- VS Code Python extension
- A Gemini API key if you want live AI generation

### 2. Open the project
Extract the project ZIP, then open the `pocketsmart_ai` folder in VS Code.

### 3. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Set at least:

```env
SECRET_KEY=replace-with-a-long-random-secret
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.8-flash
```

If `GEMINI_API_KEY` is empty, the application still runs and uses the deterministic fallback catalog. This is useful for UI/backend testing.

### 6. Start the server

```bash
python run.py
```

Open http://127.0.0.1:8000

FastAPI API documentation is available at http://127.0.0.1:8000/docs

### 7. Run tests

```bash
pytest
```

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health/configuration check |
| POST | `/register` | Create browser account |
| POST | `/login` | Start browser session |
| POST | `/logout` | End browser session |
| POST | `/token` | Issue JWT |
| GET | `/session-info` | Current authenticated user |
| GET | `/session-data` | Application/session metadata |
| POST | `/generate-home` | Home recommendations |
| POST | `/generate-party` | Party recommendations |
| POST | `/generate-jewelry` | Jewelry recommendations + optional image |
| GET | `/history` | Current user's history |
| GET | `/recommendations-details/{id}` | Retrieve one saved result |

## Real provider integrations

The supplied project document asks for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO sourcing. The documentation also explicitly calls for mock/simulated API calls during implementation. This project therefore ships with a safe catalog adapter rather than unauthorized scraping. `app/services/catalog.py` is the replacement point for official APIs or affiliate/search integrations when credentials and commercial access are available.

## Gemini behavior

The original document names Gemini 1.5 Flash Pro. The code does not hard-code that retired/legacy target; it reads `GEMINI_MODEL` from `.env`. This keeps the application maintainable as available Gemini models change.

The jewelry route sends both text and a decoded PIL image to Gemini when an image is uploaded. The uploaded image is processed in memory and is not written to disk by this application.

## Production checklist
- Use HTTPS.
- Set a strong random `SECRET_KEY` of at least 32 bytes.
- Set secure cookies behind HTTPS.
- Use PostgreSQL or another managed database instead of local SQLite for multi-instance deployment.
- Add rate limiting and request logging.
- Replace mock catalog data with official provider/affiliate APIs.
- Store secrets in a secret manager rather than `.env` on the server.
- Add CSRF protection if browser cookie authentication is exposed across origins.
