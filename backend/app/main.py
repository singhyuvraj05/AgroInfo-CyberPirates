from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Farm
from app.schemas import FarmResponse, WeatherResponse
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
                )
            )
            session.commit()
        elif demo_farm.latitude is None or demo_farm.longitude is None:
            demo_farm.latitude = 20.0059
            demo_farm.longitude = 73.7897
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
