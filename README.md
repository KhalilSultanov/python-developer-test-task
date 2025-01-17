### Основные методы (эндпойнты)

1. **POST** `/register`
    - **Описание**: Регистрация пользователя, принимает JSON вида:
      ```json
      {
        "username": "Alice"
      }
      ```  
    - **Возвращает**:
      ```json
      {
        "user_id": 1
      }
      ```

2. **POST** `/add_city`
    - **Описание**: Добавляет город пользователю, принимает JSON вида:
      ```json
      {
        "user_id": 1,
        "city_name": "London",
        "latitude": 51.5074,
        "longitude": -0.1278
      }
      ```  
    - **Возвращает**:
      ```json
      {
        "message": "Город 'London' добавлен пользователю 1"
      }
      ```

3. **GET** `/cities?user_id={id}`
    - **Описание**: Возвращает список городов у данного пользователя.
    - **Пример ответа**:
      ```json
      {
        "user_id": 1,
        "cities": [
          "London",
          "Berlin"
        ]
      }
      ```

4. **POST** `/weather`
    - **Описание**: Принимает координаты, возвращает **текущую** погоду от Open-Meteo (температуру, давление, скорость
      ветра).
    - **Пример тела запроса**:
      ```json
      {
        "latitude": 52.52,
        "longitude": 13.41
      }
      ```
    - **Пример ответа**:
      ```json
      {
        "latitude": 52.52,
        "longitude": 13.41,
        "weather": {
          "temperature_2m": 10.5,
          "surface_pressure": 1014.0,
          "wind_speed_10m": 3.2
        }
      }
      ```

5. **GET** `/hourly_weather_by_hour?user_id={id}&city_name={city}&hour={H}`
    - **Описание**: Возвращает погоду за сегодняшний день в час **H** (0..23) по UTC.
    - **Пример**:
      ```
      GET /hourly_weather_by_hour?user_id=1&city_name=London&hour=16
      ```
    - **Пример ответа**:
      ```json
      {
        "city_name": "London",
        "time": "2023-08-10T16:00:00Z",
        "weather": {
          "temperature_2m": 12.3,
          "relative_humidity_2m": 85,
          "precipitation": 0.0,
          "wind_speed_10m": 2.5
        }
      }
      ```

## Установка и запуск

1. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Запуск приложения** (скрипт `script.py`):
   ```bash
   python script.py
   ```

3. **Документация Swagger**:
   Открыть в браузере `http://127.0.0.1:8000/docs`,

## Тестирование

Тесты написаны с использованием **pytest**.
Команда для запуска тестов:

```bash
   pytest
  ```

При этом:

- Будет создана тестовая база `test_weather.db`
- Выполнятся запросы к методам API через `TestClient`
- По завершении тестов файл `test_weather.db` удалится
