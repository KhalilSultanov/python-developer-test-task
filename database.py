import sqlite3
import json
from typing import Optional, Dict, List

DB_NAME = "weather.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            weather TEXT,         
            last_updated TEXT,     
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)
        conn.commit()


def add_user(username: str) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        return cursor.lastrowid


def get_user(user_id: int) -> Optional[Dict]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "username": row[1]}
        return None


def add_city(user_id: int, city_name: str, latitude: float, longitude: float) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cities (user_id, city_name, latitude, longitude)
            VALUES (?, ?, ?, ?)
        """, (user_id, city_name, latitude, longitude))
        conn.commit()


def get_cities_for_user(user_id: int) -> List[Dict]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT city_name, latitude, longitude, weather, last_updated
            FROM cities
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

    result = []
    for row in rows:
        city_name, lat, lon, weather_json, updated = row
        weather_dict = json.loads(weather_json) if weather_json else None
        result.append({
            "city_name": city_name,
            "latitude": lat,
            "longitude": lon,
            "weather": weather_dict,
            "last_updated": updated
        })
    return result


def get_city_for_user(user_id: int, city_name: str) -> Optional[Dict]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT city_name, latitude, longitude, weather, last_updated
            FROM cities
            WHERE user_id = ? AND city_name = ?
        """, (user_id, city_name))
        row = cursor.fetchone()

    if not row:
        return None
    c_name, lat, lon, weather_json, updated = row
    weather_dict = json.loads(weather_json) if weather_json else None
    return {
        "city_name": c_name,
        "latitude": lat,
        "longitude": lon,
        "weather": weather_dict,
        "last_updated": updated
    }


def update_city_weather(user_id: int, city_name: str, weather_data: Dict) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        json_str = json.dumps(weather_data)
        updated = weather_data.get("last_updated", "")
        cursor.execute("""
            UPDATE cities
            SET weather = ?, last_updated = ?
            WHERE user_id = ? AND city_name = ?
        """, (json_str, updated, user_id, city_name))
        conn.commit()


def get_all_cities() -> List[Dict]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, city_name, latitude, longitude, weather, last_updated
            FROM cities
        """)
        rows = cursor.fetchall()

    result = []
    for row in rows:
        user_id, city_name, lat, lon, weather_json, updated = row
        weather_dict = json.loads(weather_json) if weather_json else None
        result.append({
            "user_id": user_id,
            "city_name": city_name,
            "latitude": lat,
            "longitude": lon,
            "weather": weather_dict,
            "last_updated": updated
        })
    return result
