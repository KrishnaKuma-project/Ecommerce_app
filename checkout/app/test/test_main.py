import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .. import database, models
from ..main import app

SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:krishna2005@localhost:5432/test_db_order"
)

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # test_user = models.User(
    #     username="testuser",
    #     email="testuser@example.com",
    #     password="hashedpass",
    #     mobile_no="1234567890",
    #     created_at=datetime.utcnow()
    # )
    #db.add(test_user)

    test_order = models.order_details(
        email="testuser@example.com",
        items=[{"product_id": 1, "product_name": "Test Product", "product_price": 100, "product_count": 2}],
        address="Test Address",
        payment_options="credit card",
        price=200,
        discount_price=0,
        discount_type="NONE",
    )
    db.add(test_order)
    db.commit()
    yield
    models.Base.metadata.drop_all(bind=engine)
    db.close()

def test_order_confirmation_success():
    response = client.post(
        "/order-confirmation",
        json={
            "email": "testuser@example.com",
            "address": "123 Test St",
            "payment_options": "credit card",
            "discount_code": "SK05"
        }
    )
    assert response.status_code == 200
    assert response.json()["Message"] == "Order Confirmed."

def test_order_confirmation_user_not_found():
    response = client.post(
        "/order-confirmation",
        json={
            "email": "nouser@example.com",
            "address": "123 Test St",
            "payment_options": "credit card",
            "discount_code": "SK05"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."

def test_order_confirmation_empty_cart():
    response = client.post(
        "/order-confirmation",
        json={
            "email": "emptycart@example.com",
            "address": "123 Test St",
            "payment_options": "credit card",
            "discount_code": "SK05"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Your cart is empty."

def test_order_confirmation_invalid_payment():
    response = client.post(
        "/order-confirmation",
        json={
            "email": "testuser@example.com",
            "address": "123 Test St",
            "payment_options": "bitcoin",
            "discount_code": "SK05"
        }
    )
    assert response.status_code == 404
    assert "Only [credit card" in response.json()["detail"]

def test_order_confirmation_invalid_discount():
    response = client.post(
        "/order-confirmation",
        json={
            "email": "testuser@example.com",
            "address": "123 Test St",
            "payment_options": "credit card",
            "discount_code": "INVALID"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Wrong discount code"