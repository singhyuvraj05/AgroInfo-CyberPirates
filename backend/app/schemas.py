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
