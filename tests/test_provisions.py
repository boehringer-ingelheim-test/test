import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test_provisions.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


# ── Health check ──────────────────────────────────────────────────────────────
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── Create provision ──────────────────────────────────────────────────────────
@patch("app.api.provisions._run_provision")  # prevent background Terraform call
def test_create_provision(mock_run, client):
    resp = client.post("/provisions", json={
        "name": "team-alpha",
        "owner": "alice",
        "tshirt_size": "medium",
    })
    assert resp.status_code == 202
    data = resp.json()
    assert data["name"] == "team-alpha"
    assert data["owner"] == "alice"
    assert data["tshirt_size"] == "medium"
    assert data["status"] == "pending"
    assert data["id"] is not None


@patch("app.api.provisions._run_provision")
def test_create_provision_duplicate(mock_run, client):
    payload = {"name": "team-beta", "owner": "bob", "tshirt_size": "small"}
    client.post("/provisions", json=payload)
    resp = client.post("/provisions", json=payload)
    assert resp.status_code == 409


# ── List provisions ───────────────────────────────────────────────────────────
@patch("app.api.provisions._run_provision")
def test_list_provisions(mock_run, client):
    client.post("/provisions", json={"name": "team-a", "owner": "alice", "tshirt_size": "small"})
    client.post("/provisions", json={"name": "team-b", "owner": "bob", "tshirt_size": "large"})
    resp = client.get("/provisions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


# ── Get provision ─────────────────────────────────────────────────────────────
@patch("app.api.provisions._run_provision")
def test_get_provision(mock_run, client):
    create_resp = client.post("/provisions", json={
        "name": "team-gamma", "owner": "carol", "tshirt_size": "large"
    })
    provision_id = create_resp.json()["id"]
    resp = client.get(f"/provisions/{provision_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == provision_id


def test_get_provision_not_found(client):
    resp = client.get("/provisions/nonexistent-id")
    assert resp.status_code == 404


# ── Delete provision ──────────────────────────────────────────────────────────
@patch("app.api.provisions._run_provision")
@patch("app.api.provisions._run_deprovision")
def test_delete_provision(mock_destroy, mock_run, client):
    create_resp = client.post("/provisions", json={
        "name": "team-delta", "owner": "dave", "tshirt_size": "medium"
    })
    provision_id = create_resp.json()["id"]

    # Manually set status to active so delete is allowed
    from app.models.provision import Provision
    db = TestingSessionLocal()
    record = db.query(Provision).filter(Provision.id == provision_id).first()
    record.status = "active"
    db.commit()
    db.close()

    resp = client.delete(f"/provisions/{provision_id}")
    assert resp.status_code == 202


@patch("app.api.provisions._run_provision")
def test_delete_provision_wrong_status(mock_run, client):
    create_resp = client.post("/provisions", json={
        "name": "team-epsilon", "owner": "eve", "tshirt_size": "small"
    })
    provision_id = create_resp.json()["id"]
    # Status is still "pending" — delete should be rejected
    resp = client.delete(f"/provisions/{provision_id}")
    assert resp.status_code == 409
