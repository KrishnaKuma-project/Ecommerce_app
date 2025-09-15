import pytest
import requests
from dotenv import load_dotenv
load_dotenv(".env.test",override=True)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from unittest.mock import patch
from ..import main
from .. import models,database
from ..main import app

SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:krishna2005@localhost:5432/test_db_product"
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
client = TestClient(main.app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

def test_add_to_cart_success():
    mock_user = {"email": "test@example.com", "user_type": "user"}
    mock_product = {"id": 1, "product_name": "Test Phone", "product_price": 25000}

    with patch("app.requests.get") as mock_get_user, \
         patch("app.requests.post") as mock_get_product:

        mock_get_user.return_value.status_code = 200
        mock_get_user.return_value.json.return_value = mock_user

        mock_get_product.return_value.status_code = 200
        mock_get_product.return_value.json.return_value = mock_product

        response = client.post(
            "/add-cart_iteam",
            json={
                "email": "test@example.com",
                "product_id": 1,
                "product_count": 2
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["Message"] == "Product added to cart."
    assert data["Product_name"] == "Test Phone."

def test_add_to_cart_user_not_found():
    with patch("main.app.requests.get") as mock_get_user:
        mock_get_user.return_value.status_code = 404

        response = client.post(
            "/add-cart_iteam",
            json={
                "email": "nonexist@example.com",
                "product_id": 1,
                "product_count": 2
            }
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."

def test_add_to_cart_zero_count():
    mock_user = {"email": "test@example.com", "user_type": "user"}
    mock_product = {"id": 1, "product_name": "Test Phone", "product_price": 25000}

    with patch("main.app.requests.get") as mock_get_user, \
         patch("main.app.requests.post") as mock_get_product:

        mock_get_user.return_value.status_code = 200
        mock_get_user.return_value.json.return_value = mock_user

        mock_get_product.return_value.status_code = 200
        mock_get_product.return_value.json.return_value = mock_product

        response = client.post(
            "/add-cart_iteam",
            json={
                "email": "test@example.com",
                "product_id": 1,
                "product_count": 0
            }
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Minimum 1 count to add into cart."