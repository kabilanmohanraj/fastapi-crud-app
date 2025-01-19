import pytest
from fastapi.testclient import TestClient
from backend.app.main import library_app

client = TestClient(library_app)

def authenticate():
    form_data = {
        "username": "root@test.com",
        "password": "admin"
    }
    response = client.post("/login", data=form_data)
    assert response.status_code == 200
    return response.json()["access_token"]

def test_get_books():
    access_token = authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/books?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book_by_id():
    access_token = authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 1  # Assuming book with ID 1 exists
    response = client.get(f"/books/{book_id}", headers=headers)
    if response.status_code == 200:
        assert "title" in response.json()
        assert "author" in response.json()
    else:
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"

def test_create_book():
    access_token = authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    book_data = {
        "title": "New Book",
        "author": "John Doe",
        "published_date": "2025-01-01",
        "summary": "A new book summary",
        "genre": "Fiction"
    }
    response = client.post("/books/", json=book_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == book_data["title"]

def test_update_book():
    access_token = authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 501  # Assuming book with ID 1 exists
    update_data = {
        "title": "Updated Book Title"
    }
    response = client.put(f"/books/{book_id}", json=update_data, headers=headers)
    if response.status_code == 200:
        assert response.json()["title"] == update_data["title"]
    else:
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"

def test_delete_book():
    access_token = authenticate()
    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 501  # Assuming book with ID 1 exists
    response = client.delete(f"/books/{book_id}", headers=headers)
    if response.status_code == 200:
        assert "title" in response.json()
        assert "author" in response.json()
    else:
        assert response.status_code == 404
        assert response.json()["detail"] == "Book not found"
