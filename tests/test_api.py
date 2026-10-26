import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app, get_predictor

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def fake_predictor(text: str) -> dict:
    if "bad" in text.lower() or "terrible" in text.lower():
        return {"sentiment": "NEGATIVE", "confidence": 0.99}

    return {"sentiment": "POSITIVE", "confidence": 0.99}


@pytest.fixture
def client():
    # Start every test with an empty database.
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_predictor] = lambda: fake_predictor

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == (
        "Sentiment Analysis Service is running."
    )


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_positive_text(client):
    response = client.post(
        "/analyze",
        json={"text": "I love this product!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["review"] == "I love this product!"
    assert data["sentiment"] == "POSITIVE"
    assert data["confidence"] == 0.99
    assert "id" in data
    assert "created_at" in data


def test_analyze_negative_text(client):
    response = client.post(
        "/analyze",
        json={"text": "This product is terrible."},
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == "NEGATIVE"
    assert response.json()["confidence"] == 0.99


def test_reject_empty_text(client):
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 422


def test_reject_whitespace_text(client):
    response = client.post("/analyze", json={"text": "   "})
    assert response.status_code == 422


def test_history_contains_saved_review(client):
    client.post(
        "/analyze",
        json={"text": "I love this product!"},
    )

    response = client.get("/history")
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 1
    assert history[0]["review"] == "I love this product!"
    assert history[0]["confidence"] == 0.99


def test_history_pagination(client):
    client.post("/analyze", json={"text": "First review"})
    client.post("/analyze", json={"text": "Second review"})

    response = client.get("/history?limit=1&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_history_rejects_invalid_limit(client):
    response = client.get("/history?limit=0")
    assert response.status_code == 422
