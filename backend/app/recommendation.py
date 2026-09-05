from dataclasses import dataclass

@dataclass(frozen=True)
class CropProfile:
    name: str
    ph_min: float
    ph_max: float
    nitrogen_min: float
    phosphorus_min: float
    potassium_min: float
    temperature_min: float
    temperature_max: float
    rainfall_min: float
    rainfall_max: float
    humidity_max: float
    water_requirement: str
    regenerative_benefit: str
    regenerative_score: int


@dataclass(frozen=True)
class RecommendationInputs:
    soil_ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    precipitation: float
    forecast_precipitation: float


@dataclass(frozen=True)
class CropRecommendation:
    crop: str
    suitability_score: int
    score_breakdown: dict[str, int]
    reasons: list[str]
    water_requirement: str
    regenerative_benefit: str


SUPPORTED_CROPS = (
    CropProfile(
        name="Soybean",
        ph_min=5.5,
        ph_max=7.5,
        nitrogen_min=35,
        phosphorus_min=15,
        potassium_min=100,
        temperature_min=20,
        temperature_max=32,
        rainfall_min=8,
        rainfall_max=35,
        humidity_max=85,
        water_requirement="moderate",
        regenerative_benefit="Legume rotation candidate; soil benefit is a prototype assumption.",
        regenerative_score=4,
    ),
    CropProfile(
        name="Pearl millet",
        ph_min=5.5,
        ph_max=8.0,
        nitrogen_min=25,
        phosphorus_min=10,
        potassium_min=80,
        temperature_min=24,
        temperature_max=38,
        rainfall_min=5,
        rainfall_max=25,
        humidity_max=90,
        water_requirement="low_to_moderate",
        regenerative_benefit="Diverse, heat-tolerant rotation candidate; prototype assumption.",
        regenerative_score=5,
    ),
    CropProfile(
        name="Chickpea",
        ph_min=6.0,
        ph_max=8.0,
        nitrogen_min=25,
        phosphorus_min=12,
        potassium_min=80,
        temperature_min=15,
        temperature_max=30,
        rainfall_min=3,
        rainfall_max=18,
        humidity_max=75,
        water_requirement="low",
        regenerative_benefit="Legume rotation candidate; soil benefit is a prototype assumption.",
        regenerative_score=4,
    ),
    CropProfile(
        name="Sorghum",
        ph_min=5.5,
        ph_max=8.5,
        nitrogen_min=30,
        phosphorus_min=12,
        potassium_min=90,
        temperature_min=22,
        temperature_max=36,
        rainfall_min=5,
        rainfall_max=30,
        humidity_max=90,
        water_requirement="moderate",
        regenerative_benefit="Diverse grain rotation candidate; prototype assumption.",
        regenerative_score=4,
    ),
)


def _range_score(value: float, minimum: float, maximum: float, points: int) -> int:
    return points if minimum <= value <= maximum else 0


def score_crop(profile: CropProfile, inputs: RecommendationInputs) -> CropRecommendation:
    ph_score = _range_score(inputs.soil_ph, profile.ph_min, profile.ph_max, 20)
    nitrogen_score = 10 if inputs.nitrogen >= profile.nitrogen_min else 0
    phosphorus_score = 8 if inputs.phosphorus >= profile.phosphorus_min else 0
    potassium_score = 7 if inputs.potassium >= profile.potassium_min else 0
    soil_score = ph_score + nitrogen_score + phosphorus_score + potassium_score

    temperature_score = _range_score(
        inputs.temperature, profile.temperature_min, profile.temperature_max, 20
    )
    forecast_rainfall = inputs.forecast_precipitation
    rainfall_score = _range_score(
        forecast_rainfall, profile.rainfall_min, profile.rainfall_max, 20
    )
    humidity_score = 10 if inputs.humidity <= profile.humidity_max else 0
    weather_score = temperature_score + rainfall_score + humidity_score

    reasons = [
        f"Soil pH {'fits' if ph_score else 'does not fit'} the prototype range "
        f"{profile.ph_min}-{profile.ph_max}.",
        f"Current temperature {'fits' if temperature_score else 'does not fit'} "
        f"the prototype range {profile.temperature_min}-{profile.temperature_max} °C.",
        f"Three-day forecast rainfall {'fits' if rainfall_score else 'does not fit'} "
        f"the prototype range {profile.rainfall_min}-{profile.rainfall_max} mm.",
    ]
    if nitrogen_score and phosphorus_score and potassium_score:
        reasons.append("Available soil nutrients meet the crop's prototype minimums.")
    else:
        reasons.append("One or more available soil nutrients are below prototype minimums.")

    breakdown = {
        "soil": soil_score,
        "weather": weather_score,
        "regenerative": profile.regenerative_score,
    }
    suitability_score = sum(breakdown.values())
    if suitability_score != sum(breakdown.values()):
        raise RuntimeError("Recommendation score breakdown is inconsistent")

    return CropRecommendation(
        crop=profile.name,
        suitability_score=suitability_score,
        score_breakdown=breakdown,
        reasons=reasons,
        water_requirement=profile.water_requirement,
        regenerative_benefit=profile.regenerative_benefit,
    )


def rank_crops(inputs: RecommendationInputs) -> list[CropRecommendation]:
    recommendations = [score_crop(profile, inputs) for profile in SUPPORTED_CROPS]
    return sorted(
        recommendations,
        key=lambda recommendation: (-recommendation.suitability_score, recommendation.crop),
    )[:3]
