from dataclasses import dataclass


@dataclass(frozen=True)
class AdvisoryInputs:
    crop: str
    soil_ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    precipitation: float
    forecast_precipitation: float


@dataclass(frozen=True)
class AdvisoryResult:
    risk_level: str
    score: int
    risks: list[str]
    recommendations: list[str]
    reasons: list[str]
    confidence: float


def generate_advisory(inputs: AdvisoryInputs) -> AdvisoryResult:
    """Apply transparent demo thresholds; nutrient values are assumed mg/kg."""
    score = 0
    risks: list[str] = []
    recommendations: list[str] = []
    reasons: list[str] = []

    if inputs.humidity >= 80 and inputs.forecast_precipitation >= 5:
        score += 2
        risks.append("moisture-related disease pressure")
        reasons.append(
            "High humidity and at least 5 mm of forecast rain indicate prolonged leaf moisture."
        )
        recommendations.append(
            "Inspect leaves after rain and avoid unnecessary overhead irrigation."
        )

    if inputs.forecast_precipitation >= 20:
        score += 2
        risks.append("waterlogging and field-access risk")
        reasons.append("The three-day forecast contains at least 20 mm of rain.")
        recommendations.append(
            "Keep drainage paths clear and delay field work while soil is saturated."
        )

    if inputs.temperature >= 35:
        score += 2
        risks.append("heat stress")
        reasons.append("Current temperature is at or above 35 °C.")
        recommendations.append(
            "Check crop moisture early in the day and prioritize available irrigation."
        )

    if inputs.soil_ph < 5.5 or inputs.soil_ph > 8.0:
        score += 1
        risks.append("soil pH constraint")
        reasons.append("Soil pH is outside the broad 5.5-8.0 demo range.")
        recommendations.append(
            "Confirm soil pH with a local test before applying amendments."
        )

    if inputs.nitrogen < 40:
        score += 1
        risks.append("low nitrogen indicator")
        reasons.append("Measured nitrogen is below the 40 mg/kg demo threshold.")
        recommendations.append(
            "Use a soil-test-guided nutrient plan rather than applying fertilizer blindly."
        )

    if inputs.phosphorus < 15:
        score += 1
        risks.append("low phosphorus indicator")
        reasons.append("Measured phosphorus is below the 15 mg/kg demo threshold.")
        recommendations.append(
            "Discuss a soil-test-guided phosphorus application with an agronomist."
        )

    if inputs.potassium < 100:
        score += 1
        risks.append("low potassium indicator")
        reasons.append("Measured potassium is below the 100 mg/kg demo threshold.")
        recommendations.append(
            "Review potassium needs using a current soil test and crop plan."
        )

    if score >= 4:
        risk_level = "high"
    elif score >= 2:
        risk_level = "moderate"
    else:
        risk_level = "low"

    if not reasons:
        reasons.append("The available soil and weather indicators are within demo thresholds.")
        recommendations.append("Continue routine field scouting and soil monitoring.")

    confidence = min(0.95, 0.55 + (0.05 * len(reasons)))
    return AdvisoryResult(
        risk_level=risk_level,
        score=score,
        risks=risks,
        recommendations=recommendations,
        reasons=reasons,
        confidence=round(confidence, 2),
    )
