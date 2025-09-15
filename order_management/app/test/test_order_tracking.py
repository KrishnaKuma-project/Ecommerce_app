import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from .. import database, schema

# ---- Setup test DB (SQLite in-memory for speed) ----
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database.Base.metadata.create_all(bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)


# ---------------- Mock Services ----------------
def mock_checkout_service_ok(url, json, timeout=5):
    """Simulate checkout returning orders"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            "id": 1,
            "email": json["email"],
            "items": "iPhone 16",
            "address": "123 Street",
            "payment_options": "Credit Card",
            "price": 999.99,
            "discount_price": 899.99,
            "discount_type": "Festival",
            "created_at": "2025-09-10T12:00:00"
        }
    ]
    return mock_resp


def mock_checkout_service_notfound(url, json, timeout=5):
    """Simulate checkout saying no orders"""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    return mock_resp


def mock_checkout_service_error(url, json, timeout=5):
    """Simulate checkout service failure"""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    return mock_resp


# ---------------- Test Cases ----------------
def test_order_tracking_success():
    payload = {"email": "test@example.com"}

    with patch("requests.post", side_effect=mock_checkout_service_ok):
        response = client.post("/order-tracking", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["email"] == "test@example.com"
    assert data[0]["items"] == "iPhone 16"


def test_order_tracking_not_found():
    payload = {"email": "notfound@example.com"}

    with patch("requests.post", side_effect=mock_checkout_service_notfound):
        response = client.post("/order-tracking", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Order details not found."


def test_order_tracking_service_error():
    payload = {"email": "error@example.com"}

    with patch("requests.post", side_effect=mock_checkout_service_error):
        response = client.post("/order-tracking", json=payload)

    assert response.status_code == 500
    assert "Order tracking servies error" in response.json()["detail"]

