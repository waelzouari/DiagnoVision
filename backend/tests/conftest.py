import os
os.environ["DATABASE_URL"] = "sqlite:///./test_diagnovision.db"
os.environ["DEMO_MODE"] = "true"
from fastapi.testclient import TestClient
import pytest
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as value: yield value

@pytest.fixture()
def auth(client):
    response = client.post("/api/v1/auth/login", json={"email": "doctor@diagnovision.local", "password": "DemoPass123!"})
    assert response.status_code == 200
    csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    return {"X-CSRF-Token": csrf}

