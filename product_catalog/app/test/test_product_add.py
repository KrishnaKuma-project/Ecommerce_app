import pytest
import requests
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from unittest.mock import patch
from ..main import app
from .. import schema, models, database

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
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


def test_add_product_success():
    mock_user_response = {"email": "test@example.com", "user_type": "admin"}

    with patch("app.routes.add_product.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_user_response

        response = client.post(
            "/add-product",
            json={
                "email": "admin@example.com",
                "product_name": "Test Phone",
                "product_description": "Smartphone",
                "product_categorie": "Electronics",
                "product_price": 25000,
                "product_sku": "SKU12345",
                "product_specifications": {"ram": "8GB", "storage": "128GB"},
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "product added successfully"
    assert "product_id" in data
    assert data["product_name"] == "Test Phone"

def test_add_product_user_not_found():
    with patch("app.routes.add_product.requests") as mock_requests:
        mock_requests.get.return_value.status_code = 404

        response = client.post(
            "/add-product",
            json={
                "email": "nonexist@example.com",
                "product_name": "Test Phone",
                "product_description": "Smartphone",
                "product_categorie": "Electronics",
                "product_price": 25000,
                "product_sku": "SKU12345",
                "product_specifications": {"ram": "8GB", "storage": "128GB"},
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Email ID not found in database, use your login email."


def test_add_product_non_admin_user():
    mock_user_response = {"email": "user@example.com", "user_type": "user"}

    with patch("app.routes.add_product.requests") as mock_requests:
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = mock_user_response

        response = client.post(
            "/add-product",
            json={
                "email": "user@example.com",
                "product_name": "Test Phone",
                "product_description": "Smartphone",
                "product_categorie": "Electronics",
                "product_price": 25000,
                "product_sku": "SKU12345",
                "product_specifications": {"ram": "8GB", "storage": "128GB"},
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Only admin can add product."