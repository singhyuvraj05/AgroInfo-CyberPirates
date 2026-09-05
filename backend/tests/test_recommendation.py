import unittest

from app.recommendation import (
    RecommendationInputs,
    SUPPORTED_CROPS,
    rank_crops,
    score_crop,
)


def normal_inputs() -> RecommendationInputs:
    return RecommendationInputs(
        soil_ph=6.8,
        nitrogen=55,
        phosphorus=22,
        potassium=145,
        temperature=28,
        humidity=65,
        precipitation=0,
        forecast_precipitation=8,
    )


class RecommendationTests(unittest.TestCase):
    def test_score_equals_breakdown_sum(self) -> None:
        for crop in SUPPORTED_CROPS:
            result = score_crop(crop, normal_inputs())
            self.assertEqual(
                result.suitability_score,
                sum(result.score_breakdown.values()),
            )

    def test_top_three_order_is_deterministic(self) -> None:
        first = [result.crop for result in rank_crops(normal_inputs())]
        second = [result.crop for result in rank_crops(normal_inputs())]
        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)
        self.assertEqual(first, ["Pearl millet", "Chickpea", "Sorghum"])
        scores = [result.suitability_score for result in rank_crops(normal_inputs())]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_only_supported_crops_are_returned(self) -> None:
        result = rank_crops(normal_inputs())
        self.assertTrue(all(item.crop in {crop.name for crop in SUPPORTED_CROPS} for item in result))


if __name__ == "__main__":
    unittest.main()
