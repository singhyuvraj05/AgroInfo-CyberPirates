import unittest

from app.vegetation import (
    classify_ndvi,
    classify_trend,
    get_vegetation,
)


class VegetationTests(unittest.TestCase):
    def test_ndvi_classifications(self) -> None:
        self.assertEqual(classify_ndvi(0.29), "stressed")
        self.assertEqual(classify_ndvi(0.30), "moderate")
        self.assertEqual(classify_ndvi(0.55), "moderate")
        self.assertEqual(classify_ndvi(0.56), "healthy")

    def test_trend_classifications(self) -> None:
        self.assertEqual(classify_trend(0.60, 0.50), "improving")
        self.assertEqual(classify_trend(0.52, 0.50), "stable")
        self.assertEqual(classify_trend(0.45, 0.50), "declining")

    def test_same_farm_has_deterministic_output(self) -> None:
        self.assertEqual(get_vegetation(1), get_vegetation(1))

    def test_demo_result_is_synthetic(self) -> None:
        result = get_vegetation(1)
        self.assertTrue(result.is_synthetic)
        self.assertEqual(result.ndvi, 0.56)
        self.assertEqual(result.previous_ndvi, 0.48)
        self.assertEqual(result.vegetation_status, "healthy")
        self.assertEqual(result.trend, "improving")


if __name__ == "__main__":
    unittest.main()
