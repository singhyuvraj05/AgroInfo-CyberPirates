from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class CooperativeInsightCreate(BaseModel):
    publisher_state: str = Field(min_length=1, max_length=80)
    crop: str = Field(min_length=1, max_length=80)
    insight_type: Literal[
        "advisory", "crop_recommendation", "vegetation", "disease_screening"
    ]
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1)
    version: str = Field(min_length=1, max_length=40)
    metric_label: str | None = Field(default=None, max_length=80)
    metric_value: float | None = None


class CooperativeInsightReuse(BaseModel):
    target_state: str = Field(min_length=1, max_length=80)
    adaptation_note: str = Field(min_length=1)


class CooperativeInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publisher_state: str
    crop: str
    insight_type: str
    title: str
    description: str
    version: str
    metric_label: str | None
    metric_value: float | None
    status: Literal["published", "adapted"]
    source_insight_id: int | None
    adaptation_note: str | None
    created_at: datetime
