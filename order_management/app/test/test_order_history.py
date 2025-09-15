import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app  

client = TestClient(app)

def mock_get_user_details_ok(url, timeout=5):
    if "user_management" in url:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"email": "test@example.com", "id": 1}
        return mock_resp
    raise ValueError("Unexpected GET URL:", url)

def mock_post_order_details_ok(url, json, timeout=5):
    if "checkout" in url and "/order-history" in url:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {
                "id": 101,
                "email": "test@example.com",
                "items": [{"product": "Laptop", "qty": 1}],
                "address": "Bangalore",
                "payment_options": "UPI",
                "price": 50000,
                "discount_price": 48000,
                "discount_type": "Festival",
                "created_at": "2025-09-13T10:00:00",
            }
        ]
        return mock_resp
    raise ValueError("Unexpected POST URL:", url)


@pytest.fixture
def patch_requests():
    with patch("requests.get", side_effect=mock_get_user_details_ok):
        with patch("requests.post", side_effect=mock_post_order_details_ok):
            yield


def test_order_history_success(patch_requests):
    response = client.post(
        "/order-history",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data[0]["id"] == 101
    assert data[0]["email"] == "test@example.com"
    assert data[0]["price"] == 50000
    assert data[0]["discount_price"] == 48000


def test_order_history_user_not_found():
    def mock_get_user_not_found(url, timeout=5):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        return mock_resp

    with patch("requests.get", side_effect=mock_get_user_not_found):
        response = client.post(
            "/order-history",
            json={"email": "notfound@example.com"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Enter the user email to view order history."


def test_order_history_no_orders(patch_requests):
    def mock_post_no_orders(url, json, timeout=5):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        return mock_resp

    with patch("requests.post", side_effect=mock_post_no_orders):
        response = client.post(
            "/order-history",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "No order detail"