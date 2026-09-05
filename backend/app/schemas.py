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


class AdvisoryResponse(BaseModel):
    farm_id: int
    crop: str
    risk_level: str
    score: int
    risks: list[str]
    recommendations: list[str]
    reasons: list[str]
    confidence: float


class CropRecommendationResponse(BaseModel):
    crop: str
    suitability_score: int
    score_breakdown: dict[str, int]
    reasons: list[str]
    water_requirement: str
    regenerative_benefit: str


class RecommendationResponse(BaseModel):
    farm_id: int
    location: str
    assumptions: list[str]
    recommendations: list[CropRecommendationResponse]


class VegetationResponse(BaseModel):
    farm_id: int
    ndvi: float
    previous_ndvi: float
    vegetation_status: str
    trend: str
    is_synthetic: bool
    note: str


class DiseaseScreeningResponse(BaseModel):
    status: str
    observation: str
    certainty: str
    next_step: str
    is_demo: bool
    disclaimer: str
