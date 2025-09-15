import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from .. import database, models
from .. import main

SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_cart.db"
)

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_TEST_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

main.app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(main.app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def create_cart_item():
    db = TestingSessionLocal()
    cart_item = models.cart_list(
        email="testuser@example.com",
        product_id=1,
        product_name="Test Product",
        product_price=1000,
        product_count=2
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    db.close()
    return cart_item

def test_remove_cart_item(create_cart_item):
    response = client.post(
        "/remove-cart_item",
        json={"cart_id": create_cart_item.id}
    )
    assert response.status_code == 200
    assert f"Cart item with id {create_cart_item.id} deleted successfully." in response.json()["message"]

def test_remove_cart_item_not_found():
    response = client.post(
        "/remove-cart_item",
        json={"cart_id": 1}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Cart item not found."

@pytest.fixture
def create_multiple_cart_items():
    db = TestingSessionLocal()
    items = []
    for i in range(3):
        item = models.cart_list(
            email="testuser@example.com",
            product_id=i+1,
            product_name=f"Product {i+1}",
            product_price=100*(i+1),
            product_count=i+1
        )
        db.add(item)
        items.append(item)
    db.commit()
    for item in items:
        db.refresh(item)
    db.close()
    return items

def test_remove_full_cart(create_multiple_cart_items):
    response = client.post(
        "/remove-all_cart_item",
        json={"email": "testuser@example.com"}
    )
    assert response.status_code == 200
    assert "All 3 cart items for testuser@example.com deleted successfully." in response.json()["message"]

def test_remove_full_cart_not_found():
    response = client.post(
        "/remove-all_cart_item",
        json={"email": "nouser@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "No cart item found."
