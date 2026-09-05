import unittest

from pydantic import ValidationError

from app.schemas import FarmCreate


def valid_payload() -> dict[str, object]:
    return {
        "name": "Test Farm",
        "state": "Maharashtra",
        "district": "Nashik",
        "village": "Sinnar",
        "area_acres": 4.5,
        "soil_type": "Black cotton soil",
        "current_crop": "Soybean",
        "latitude": 20.0059,
        "longitude": 73.7897,
        "soil_ph": 6.8,
        "nitrogen": 55,
        "phosphorus": 22,
        "potassium": 145,
    }


class FarmCreateValidationTests(unittest.TestCase):
    def test_valid_farm_creation_payload(self) -> None:
        farm = FarmCreate(**valid_payload())
        self.assertEqual(farm.name, "Test Farm")

    def test_invalid_coordinates_are_rejected(self) -> None:
        for field, value in (("latitude", 91), ("longitude", 181)):
            with self.subTest(field=field):
                payload = valid_payload()
                payload[field] = value
                with self.assertRaises(ValidationError):
                    FarmCreate(**payload)

    def test_invalid_area_ph_and_negative_nutrients_are_rejected(self) -> None:
        for field, value in (
            ("area_acres", 0),
            ("soil_ph", 14.1),
            ("nitrogen", -1),
            ("phosphorus", -1),
            ("potassium", -1),
        ):
            with self.subTest(field=field):
                payload = valid_payload()
                payload[field] = value
                with self.assertRaises(ValidationError):
                    FarmCreate(**payload)

    def test_required_fields_are_rejected_when_missing(self) -> None:
        payload = valid_payload()
        del payload["current_crop"]
        with self.assertRaises(ValidationError):
            FarmCreate(**payload)


if __name__ == "__main__":
    unittest.main()
