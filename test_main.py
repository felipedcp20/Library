import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock

client = TestClient(app)


def test_version():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}


def test_login():
    response = client.post(
        "/token",
        data={"username": "mock", "password": "secret"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_password():
    response = client.post("/token", data={"username": "felipeandrod", "password": "incorrect"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_read_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert "books" in response.json()

