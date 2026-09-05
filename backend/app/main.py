from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Farm
from app.schemas import FarmResponse


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
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
                )
            )
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
