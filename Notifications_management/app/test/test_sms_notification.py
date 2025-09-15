import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from .. import database, models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

database.Base.metadata.create_all(bind=engine)
app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def clear_tables():
    """Clear notification_table before each test"""
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    yield


def test_otp_sms_success(monkeypatch):
    def mock_user_details(email: str):
        return {"email": email, "user_type": "customer", "mobile": "9876543210"}

    monkeypatch.setattr("app.routers.notifications.get_user_details", mock_user_details)

    def mock_send_otp_sms(mobile, otp):
        print(f"Mock send SMS to {mobile} with OTP {otp}")

    monkeypatch.setattr("app.routers.notifications.send_otp_sms", mock_send_otp_sms)

    response = client.post("/otp_sms", json={"email": "testuser@gmail.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "OTP generated and sent successfully via Twilio"


def test_otp_sms_user_not_found(monkeypatch):
    def mock_user_details(email: str):
        return None

    monkeypatch.setattr("app.routers.notifications.get_user_details", mock_user_details)

    response = client.post("/otp_sms", json={"email": "nouser@gmail.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_otp_sms_no_mobile(monkeypatch):
    def mock_user_details(email: str):
        return {"email": email, "user_type": "customer", "mobile": None}

    monkeypatch.setattr("app.routers.notifications.get_user_details", mock_user_details)

    response = client.post("/otp_sms", json={"email": "nomobile@gmail.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "MObile number not found in the database."