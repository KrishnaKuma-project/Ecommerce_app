import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
import os
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

from ..main import app, models, database
from .. import product_adding, product_remove

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
    db = TestingSessionLocal()
    new_product = models.product_table(
        product_name="Test Product",
        product_description="Test Desc",
        product_categorie="Electronics",
        product_price=1000,
        product_sku="SKU100",
        product_specifications={"ram": "4GB"}
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    yield new_product.id
    models.Base.metadata.drop_all(bind=engine)
    db.close()

def test_remove_product_success(setup_test_db):
    product_id = setup_test_db
    mock_user = {"email": "admin@example.com", "user_type": "admin"}

    with patch("app.product_remove.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_user

        response = client.post(
            "/remove-product",
            json={"email": "admin@example.com", "product_id": product_id}
        )

    assert response.status_code == 200
    assert response.json()["Message"] == f"Product {product_id} delete successfully"

def test_remove_product_not_found():
    mock_user = {"email": "admin@example.com", "user_type": "admin"}

    with patch("app.product_remove.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_user

        response = client.post(
            "/remove-product",
            json={"email": "admin@example.com", "product_id": 9999}
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_remove_product_non_admin(setup_test_db):
    product_id = setup_test_db
    mock_user = {"email": "user@example.com", "user_type": "user"}

    with patch("app.product_remove.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_user

        response = client.post(
            "/remove-product",
            json={"email": "user@example.com", "product_id": product_id}
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin can add product."

def test_remove_product_user_not_found():
    with patch("app.product_remove.requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        response = client.post(
            "/remove-product",
            json={"email": "nonexist@example.com", "product_id": 1}
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Email ID not found in database, use your login email."
