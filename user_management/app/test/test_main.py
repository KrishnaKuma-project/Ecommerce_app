import pytest 
from fastapi.testclient import TestClient
from ..main import app
from .. import models, database, password_hashing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:krishna2005@localhost:5432/test_db_users"
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

def test_signup_success():
    response = client.post("/signup", json={
        "name": "Test User",
        "username": "testuser",
        "password": "test123",
        "email": "test@example.com",
        "mobile": "1234567890",
        "user_type": "customer"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

def test_signup_existing_email():
    response = client.post("/signup", json={
        "name": "Another User",
        "username": "anotheruser",
        "password": "test123",
        "email": "test@example.com", 
        "mobile": "0987654321",
        "user_type": "customer"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email Already in database."

def test_login_success():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["Message"] == "Login Successfully"
    assert "Access_token" in data

def test_login_wrong_email():
    response = client.post("/login", json={
        "email": "wrong@example.com",
        "password": "test123"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Email ID not found in database."

def test_login_wrong_password():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "You given invalid Password."

def test_logout_success():
    client.post("/login", json={"email": "test@example.com", "password": "test123"})
    
    response = client.post("/logout", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["Message"] == "You logout process successfull."

def test_logout_already_logged_out():
    response = client.post("/logout", json={"email": "notlogged@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User status already logout."