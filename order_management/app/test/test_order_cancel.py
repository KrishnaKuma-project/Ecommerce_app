import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import database, models, schema
from ..main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database.Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)

def mock_user_service_ok(url, timeout=5):
    """Simulate user service success"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"email": "test@example.com", "user_type": "customer"}
    return mock_resp

def mock_user_service_notfound(url, timeout=5):
    """Simulate user not found"""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    return mock_resp

def mock_checkout_service_ok(url, json, timeout=5):
    """Simulate checkout service success"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"order_id": json["order_id"], "status": "Cancelled"}
    return mock_resp

def mock_checkout_service_notfound(url, json, timeout=5):
    """Simulate checkout service says order not found"""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    return mock_resp

def test_order_cancel_success():
    payload = {"email": "test@example.com", "order_id": 123}

    with patch("requests.get", side_effect=mock_user_service_ok), \
         patch("requests.post", side_effect=mock_checkout_service_ok):
        response = client.post("/order-cancel", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Cancelled"
    assert data["order_id"] == 123


def test_order_cancel_user_not_found():
    payload = {"email": "notfound@example.com", "order_id": 123}

    with patch("requests.get", side_effect=mock_user_service_notfound):
        response = client.post("/order-cancel", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found, use login email."


def test_order_cancel_order_not_found():
    payload = {"email": "test@example.com", "order_id": 999}

    with patch("requests.get", side_effect=mock_user_service_ok), \
         patch("requests.post", side_effect=mock_checkout_service_notfound):
        response = client.post("/order-cancel", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found."
