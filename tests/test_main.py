import pytest
from fastapi.testclient import TestClient
import os

import database
from script import app

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    test_db = "test_weather.db"
    old_db_name = database.DB_NAME
    database.DB_NAME = test_db
    database.init_db()
    yield
    if os.path.exists(test_db):
        os.remove(test_db)
    database.DB_NAME = old_db_name


def test_register_user():
    response = client.post("/register", json={"username": "John"})
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_register_user_no_body():
    response = client.post("/register", json={})
    assert response.status_code == 422


def test_add_city_ok():
    resp_user = client.post("/register", json={"username": "Alice"})
    user_id = resp_user.json()["user_id"]
    city_data = {
        "user_id": user_id,
        "city_name": "London",
        "latitude": 51.5074,
        "longitude": -0.1278
    }
    response = client.post("/add_city", json=city_data)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "добавлен пользователю" in data["message"]


def test_add_city_for_unknown_user():
    city_data = {
        "user_id": 999999,
        "city_name": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    response = client.post("/add_city", json=city_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Пользователь не найден"


def test_get_cities():
    resp_user = client.post("/register", json={"username": "Bob"})
    user_id = resp_user.json()["user_id"]
    client.post("/add_city", json={
        "user_id": user_id,
        "city_name": "City1",
        "latitude": 10.0,
        "longitude": 20.0
    })
    client.post("/add_city", json={
        "user_id": user_id,
        "city_name": "City2",
        "latitude": 30.0,
        "longitude": 40.0
    })
    response = client.get(f"/cities?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert len(data["cities"]) == 2
    assert "City1" in data["cities"]
    assert "City2" in data["cities"]


def test_weather_endpoint():
    payload = {"latitude": 52.52, "longitude": 13.41}
    response = client.post("/weather", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "weather" in data
    assert "temperature_2m" in data["weather"]
    assert "surface_pressure" in data["weather"]
    assert "wind_speed_10m" in data["weather"]


def test_hourly_weather_by_hour_not_found():
    response = client.get("/hourly_weather_by_hour", params={
        "user_id": 9999,
        "city_name": "NoCity",
        "hour": 16
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Пользователь не найден"
