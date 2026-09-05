import unittest

from app.advisory import AdvisoryInputs, generate_advisory


def inputs(**overrides: float | str) -> AdvisoryInputs:
    values: dict[str, float | str] = {
        "crop": "Soybean",
        "soil_ph": 6.8,
        "nitrogen": 55.0,
        "phosphorus": 22.0,
        "potassium": 145.0,
        "temperature": 28.0,
        "humidity": 60.0,
        "precipitation": 0.0,
        "forecast_precipitation": 2.0,
    }
    values.update(overrides)
    return AdvisoryInputs(**values)


class AdvisoryRulesTests(unittest.TestCase):
    def test_normal_conditions_have_low_risk(self) -> None:
        result = generate_advisory(inputs())
        self.assertEqual(result.risk_level, "low")
        self.assertEqual(result.score, 0)

    def test_moisture_conditions_raise_disease_pressure(self) -> None:
        result = generate_advisory(
            inputs(humidity=85.0, forecast_precipitation=8.0)
        )
        self.assertIn("moisture-related disease pressure", result.risks)
        self.assertEqual(result.risk_level, "moderate")

    def test_multiple_stresses_are_high_risk(self) -> None:
        result = generate_advisory(
            inputs(
                humidity=85.0,
                forecast_precipitation=25.0,
                temperature=36.0,
                soil_ph=5.0,
            )
        )
        self.assertEqual(result.risk_level, "high")
        self.assertGreaterEqual(result.score, 4)


if __name__ == "__main__":
    unittest.main()
