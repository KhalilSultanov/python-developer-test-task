from pydantic import BaseModel, confloat


class User(BaseModel):
    username: str


class City(BaseModel):
    user_id: int
    city_name: str
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)


class Coordinates(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
