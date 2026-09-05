from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.advisory import AdvisoryInputs, generate_advisory
from app.config import settings
from app.database import Base, engine, get_db
from app.models import Farm
from app.recommendation import RecommendationInputs, rank_crops
from app.schemas import (
    AdvisoryResponse,
    FarmResponse,
    RecommendationResponse,
    VegetationResponse,
    WeatherResponse,
)
from app.vegetation import get_vegetation
from app.weather import WeatherServiceError, get_weather


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    existing_columns = {
        column["name"] for column in inspect(engine).get_columns("farms")
    }
    with engine.begin() as connection:
        if "latitude" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN latitude FLOAT NULL"))
        if "longitude" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN longitude FLOAT NULL"))
        if "soil_ph" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN soil_ph FLOAT NULL"))
        if "nitrogen" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN nitrogen FLOAT NULL"))
        if "phosphorus" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN phosphorus FLOAT NULL"))
        if "potassium" not in existing_columns:
            connection.execute(text("ALTER TABLE farms ADD COLUMN potassium FLOAT NULL"))

    with Session(engine) as session:
        demo_farm = session.scalar(select(Farm).where(Farm.id == 1))
        if demo_farm is None:
            session.add(
                Farm(
                    id=1,
                    name="Demo Green Valley Farm",
                    state="Maharashtra",
                    district="Nashik",
                    village="Sinnar",
                    area_acres=4.5,
                    soil_type="Black cotton soil",
                    current_crop="Soybean",
                    latitude=20.0059,
                    longitude=73.7897,
                    soil_ph=6.8,
                    nitrogen=55,
                    phosphorus=22,
                    potassium=145,
                )
            )
            session.commit()
        else:
            if demo_farm.latitude is None or demo_farm.longitude is None:
                demo_farm.latitude = 20.0059
                demo_farm.longitude = 73.7897
            if demo_farm.soil_ph is None:
                demo_farm.soil_ph = 6.8
            if demo_farm.nitrogen is None:
                demo_farm.nitrogen = 55
            if demo_farm.phosphorus is None:
                demo_farm.phosphorus = 22
            if demo_farm.potassium is None:
                demo_farm.potassium = 145
            session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="AgroInfo API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/farms/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)) -> Farm:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@app.get("/api/weather/{farm_id}", response_model=WeatherResponse)
def get_farm_weather(farm_id: int, db: Session = Depends(get_db)) -> WeatherResponse:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=422, detail="Farm coordinates are missing")

    try:
        weather = get_weather(farm.latitude, farm.longitude)
    except WeatherServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    current = weather["current"]
    daily = weather["daily"]
    forecast = [
        {
            "date": date,
            "precipitation_sum": precipitation,
            "precipitation_probability_max": probability,
        }
        for date, precipitation, probability in zip(
            daily["time"],
            daily["precipitation_sum"],
            daily.get("precipitation_probability_max", [None] * len(daily["time"])),
        )
    ]
    return WeatherResponse(
        farm_id=farm.id,
        location=", ".join((farm.village, farm.district, farm.state)),
        temperature=current["temperature_2m"],
        humidity=current["relative_humidity_2m"],
        precipitation=current["precipitation"],
        forecast=forecast,
    )


@app.get("/api/advisory/{farm_id}", response_model=AdvisoryResponse)
def get_farm_advisory(
    farm_id: int, db: Session = Depends(get_db)
) -> AdvisoryResponse:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    soil_values = (farm.soil_ph, farm.nitrogen, farm.phosphorus, farm.potassium)
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=422, detail="Farm coordinates are missing")
    if any(value is None for value in soil_values):
        raise HTTPException(status_code=422, detail="Farm soil data is incomplete")

    try:
        weather = get_weather(farm.latitude, farm.longitude)
    except WeatherServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    daily = weather["daily"]
    inputs = AdvisoryInputs(
        crop=farm.current_crop,
        soil_ph=farm.soil_ph,
        nitrogen=farm.nitrogen,
        phosphorus=farm.phosphorus,
        potassium=farm.potassium,
        temperature=weather["current"]["temperature_2m"],
        humidity=weather["current"]["relative_humidity_2m"],
        precipitation=weather["current"]["precipitation"],
        forecast_precipitation=sum(daily["precipitation_sum"]),
    )
    result = generate_advisory(inputs)
    return AdvisoryResponse(
        farm_id=farm.id,
        crop=farm.current_crop,
        risk_level=result.risk_level,
        score=result.score,
        risks=result.risks,
        recommendations=result.recommendations,
        reasons=result.reasons,
        confidence=result.confidence,
    )


@app.get(
    "/api/recommendations/{farm_id}",
    response_model=RecommendationResponse,
)
def get_farm_recommendations(
    farm_id: int, db: Session = Depends(get_db)
) -> RecommendationResponse:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    soil_values = (farm.soil_ph, farm.nitrogen, farm.phosphorus, farm.potassium)
    if farm.latitude is None or farm.longitude is None:
        raise HTTPException(status_code=422, detail="Farm coordinates are missing")
    if any(value is None for value in soil_values):
        raise HTTPException(status_code=422, detail="Farm soil data is incomplete")

    try:
        weather = get_weather(farm.latitude, farm.longitude)
    except WeatherServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    current = weather["current"]
    daily = weather["daily"]
    recommendations = rank_crops(
        RecommendationInputs(
            soil_ph=farm.soil_ph,
            nitrogen=farm.nitrogen,
            phosphorus=farm.phosphorus,
            potassium=farm.potassium,
            temperature=current["temperature_2m"],
            humidity=current["relative_humidity_2m"],
            precipitation=current["precipitation"],
            forecast_precipitation=sum(daily["precipitation_sum"]),
        )
    )
    return RecommendationResponse(
        farm_id=farm.id,
        location=", ".join((farm.village, farm.district, farm.state)),
        assumptions=[
            "Suitability scores are deterministic MVP heuristics, not probabilities.",
            "Water availability is unknown and is not scored in V1.",
            "Location is contextual only; no planting season is inferred.",
            "Crop profiles and regenerative descriptions are prototype assumptions.",
        ],
        recommendations=[
            {
                "crop": recommendation.crop,
                "suitability_score": recommendation.suitability_score,
                "score_breakdown": recommendation.score_breakdown,
                "reasons": recommendation.reasons,
                "water_requirement": recommendation.water_requirement,
                "regenerative_benefit": recommendation.regenerative_benefit,
            }
            for recommendation in recommendations
        ],
    )


@app.get(
    "/api/vegetation/{farm_id}",
    response_model=VegetationResponse,
)
def get_farm_vegetation(
    farm_id: int, db: Session = Depends(get_db)
) -> VegetationResponse:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")

    vegetation = get_vegetation(farm.id)
    return VegetationResponse(
        farm_id=farm.id,
        ndvi=vegetation.ndvi,
        previous_ndvi=vegetation.previous_ndvi,
        vegetation_status=vegetation.vegetation_status,
        trend=vegetation.trend,
        is_synthetic=vegetation.is_synthetic,
        note=vegetation.note,
    )
