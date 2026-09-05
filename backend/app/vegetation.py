from dataclasses import dataclass


SYNTHETIC_NDVI_BY_FARM = {
    1: {"ndvi": 0.56, "previous_ndvi": 0.48},
}


@dataclass(frozen=True)
class VegetationResult:
    ndvi: float
    previous_ndvi: float
    vegetation_status: str
    trend: str
    is_synthetic: bool
    note: str


def classify_ndvi(ndvi: float) -> str:
    if ndvi < 0.30:
        return "stressed"
    if ndvi <= 0.55:
        return "moderate"
    return "healthy"


def classify_trend(current_ndvi: float, previous_ndvi: float) -> str:
    change = current_ndvi - previous_ndvi
    if change > 0.03:
        return "improving"
    if change < -0.03:
        return "declining"
    return "stable"


def get_vegetation(farm_id: int) -> VegetationResult:
    values = SYNTHETIC_NDVI_BY_FARM.get(
        farm_id,
        {"ndvi": 0.56, "previous_ndvi": 0.48},
    )
    ndvi = values["ndvi"]
    previous_ndvi = values["previous_ndvi"]
    return VegetationResult(
        ndvi=ndvi,
        previous_ndvi=previous_ndvi,
        vegetation_status=classify_ndvi(ndvi),
        trend=classify_trend(ndvi, previous_ndvi),
        is_synthetic=True,
        note=(
            "Prototype synthetic NDVI demonstration; not satellite or "
            "field-measured data."
        ),
    )
