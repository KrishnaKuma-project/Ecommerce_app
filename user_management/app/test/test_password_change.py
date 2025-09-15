import pytest
from fastapi.testclient import TestClient
from user_management.app import models, password_hashing
from user_management.app.main import app
from user_management.app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    # Clean previous users
    db.query(models.user_details).delete()
    db.commit()

    hashed_pw = password_hashing.get_password_hashed("oldpassword")
    user = models.user_details(
        username="testuser",
        email="test@example.com",
        mobile="1234567890",
        password=hashed_pw,
        user_type="user"
    )
    db.add(user)
    db.commit()
    yield user
    db.close()

def test_password_change_success(test_user):
    response = client.post(
        "/password-change",
        json={
            "email": "test@example.com",
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password changed successfully"


def test_password_change_wrong_old_password(test_user):
    response = client.post(
        "/password-change",
        json={
            "email": "test@example.com",
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Old password is incorrect."


def test_password_change_mismatch_new_confirm(test_user):
    response = client.post(
        "/password-change",
        json={
            "email": "test@example.com",
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "New password and Confirm password should be same."


def test_password_change_user_not_found():
    response = client.post(
        "/password-change",
        json={
            "email": "nouser@example.com",
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
