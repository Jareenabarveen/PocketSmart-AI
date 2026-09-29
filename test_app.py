import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["GEMINI_API_KEY"] = ""
from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        r = client.get('/health')
        assert r.status_code == 200
        assert r.json()['status'] == 'ok'


def test_register_login_and_home():
    with TestClient(app) as client:
        r = client.post('/register', data={'full_name':'Test User','email':'test@example.com','password':'password123'}, follow_redirects=False)
        assert r.status_code == 303
        r = client.get('/dashboard')
        assert r.status_code == 200
        r = client.post('/generate-home', json={'budget':50000,'city':'Chennai','style':'modern','rooms':['Living Room'],'items':{},'notes':''})
        assert r.status_code == 200
        body = r.json()
        assert body['planner'] == 'home'
        assert body['budget'] == 50000
        assert len(body['recommendations']) >= 1


def test_party_and_jewelry_auth():
    with TestClient(app) as client:
        client.post('/login', data={'email':'test@example.com','password':'password123'}, follow_redirects=False)
        r = client.post('/generate-party', json={'budget':75000,'city':'Chennai','event_type':'birthday','guests':50,'venue':'home','date':'','notes':''})
        assert r.status_code == 200
        r = client.post('/generate-jewelry', data={'budget':'5000','occasion':'festive','style':'traditional','outfit_notes':''})
        assert r.status_code == 200
        assert r.json()['planner'] == 'jewelry'
