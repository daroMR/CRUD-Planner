import pytest
import os
import sys
from fastapi.testclient import TestClient

# Sobreescribir DATABASE_URL para usar una local de test antes de importar main
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    # Eliminar DB de test si existe antes de empezar
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    yield
    # Limpieza final opcional
    if os.path.exists("./test.db"):
        os.remove("./test.db")

def test_read_root():
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307 
        assert response.headers["location"] == "/app/index.html"

def test_auth_status_not_authenticated():
    with TestClient(app) as client:
        response = client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False

def test_get_plans_fallback_local():
    with TestClient(app) as client:
        response = client.get("/plans")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_create_plan_local():
    with TestClient(app) as client:
        plan_data = {"name": "Test Plan Local"}
        response = client.post("/plans", json=plan_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Plan Local"
        assert "id" in data
