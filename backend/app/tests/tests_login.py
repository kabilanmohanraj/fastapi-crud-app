import pytest
from fastapi.testclient import TestClient
from backend.app.main import library_app

client = TestClient(library_app)

def test_user_login_success():
    form_data = {
        "username": "root@test.com",
        "password": "admin"
    }

    response = client.post("/login", data=form_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_login_incorrect_username():
    form_data = {
        "username": "nonexistent@example.com",
        "password": "admin"
    }

    response = client.post("/login", data=form_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect username or password"

def test_user_login_incorrect_password():
    form_data = {
        "username": "root@test.com",
        "password": "wrongpassword"
    }

    response = client.post("/login", data=form_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect username or password"
