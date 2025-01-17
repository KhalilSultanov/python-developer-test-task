import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException

from models import User, City, Coordinates
import database
from weather_service import fetch_weather_data, get_weather_by_hour

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def lifespan(app: FastAPI):
    database.init_db()
    task = asyncio.create_task(update_weather_task())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


async def update_weather_task():
    """
    Бесконечный цикл: раз в 15 минут пробегаем по всем городам из БД,
    тянем новую погоду из Open-Meteo и обновляем в БД.
    """
    while True:
        try:
            all_cities = database.get_all_cities()
            for city in all_cities:
                try:
                    w_data = await fetch_weather_data(city["latitude"], city["longitude"])
                    w_data["last_updated"] = datetime.now().isoformat()
                    database.update_city_weather(city["user_id"], city["city_name"], w_data)
                except Exception as e:
                    error_data = {"error": f"Не удалось обновить погоду: {str(e)}"}
                    database.update_city_weather(city["user_id"], city["city_name"], error_data)
        except Exception as e:
            logger.exception("Ошибка в update_weather_task")
        await asyncio.sleep(900)


@app.post("/register")
async def register_user_endpoint(user: User):
    """
    Регистрация пользователя, возвращает user_id.
    """
    user_id = database.add_user(user.username)
    return {"user_id": user_id}


@app.post("/add_city")
async def add_city_endpoint(city: City):
    """
    Принимает user_id, название города, координаты, добавляет их в БД для пользователя.
    """
    user_obj = database.get_user(city.user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    database.add_city(city.user_id, city.city_name, city.latitude, city.longitude)
    return {"message": f"Город '{city.city_name}' добавлен пользователю {city.user_id}"}


@app.get("/cities")
async def get_city_names(user_id: int):
    """
    Возвращает список городов для введенного user_id, для которых доступен прогноз погоды.
    """
    user_obj = database.get_user(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    cities = database.get_cities_for_user(user_id)
    city_names = [c["city_name"] for c in cities]
    return {"user_id": user_id, "cities": city_names}


@app.post("/weather")
async def get_weather_endpoint(coords: Coordinates):
    """
    Принимает координаты, возвращает текущую погоду.
    """
    weather = await fetch_weather_data(coords.latitude, coords.longitude)
    return {
        "latitude": coords.latitude,
        "longitude": coords.longitude,
        "weather": weather
    }


@app.get("/hourly_weather_by_hour")
async def get_hourly_weather_by_hour(
        user_id: int,
        city_name: str,
        hour: int,
        params: str = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
):
    """
    Принимаем user_id, название города, час (0...23).
    Собираем ISO-строку для текущего дня.
    Запрашиваем погоду на введенный час.
    """
    if not (0 <= hour <= 23):
        raise HTTPException(status_code=400, detail="Час должен быть в диапазоне [0..23].")

    user_obj = database.get_user(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    city = database.get_city_for_user(user_id, city_name)
    if not city:
        raise HTTPException(
            status_code=404,
            detail=f"Город '{city_name}' не найден у пользователя {user_id}"
        )

    today_utc = datetime.now().date()
    hour_str = f"{today_utc.isoformat()}T{hour:02d}:00:00Z"

    hourly_params_list = [p.strip() for p in params.split(",") if p.strip()]

    weather_data = await get_weather_by_hour(
        latitude=city["latitude"],
        longitude=city["longitude"],
        hour_str=hour_str,
        hourly_params_list=hourly_params_list
    )

    return {
        "city_name": city_name,
        "time": hour_str,
        "weather": weather_data
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
