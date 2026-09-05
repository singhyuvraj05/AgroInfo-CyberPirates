from pydantic import BaseModel, ConfigDict


class FarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    state: str
    district: str
    village: str
    area_acres: float
    soil_type: str
    current_crop: str


class ForecastDay(BaseModel):
    date: str
    precipitation_sum: float
    precipitation_probability_max: int | None


class WeatherResponse(BaseModel):
    farm_id: int
    location: str
    temperature: float
    humidity: int
    precipitation: float
    forecast: list[ForecastDay]
