import io
import unittest

from PIL import Image

from app.disease import (
    DemoDiseaseAnalyzer,
    ImageValidationError,
    MAX_IMAGE_SIZE,
    UNCERTAIN_MESSAGE,
    decode_image,
    validate_image_upload,
)


def make_image(image_format: str, size: tuple[int, int] = (100, 100)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color="green").save(buffer, format=image_format)
    return buffer.getvalue()


class DiseaseScreeningTests(unittest.TestCase):
    def test_valid_jpeg_decodes(self) -> None:
        image = decode_image(make_image("JPEG"))
        self.assertEqual(image.format, "JPEG")

    def test_valid_png_decodes(self) -> None:
        image = decode_image(make_image("PNG"))
        self.assertEqual(image.format, "PNG")

    def test_valid_uploads_are_accepted(self) -> None:
        self.assertEqual(
            validate_image_upload(make_image("JPEG"), "image/jpeg").format,
            "JPEG",
        )
        self.assertEqual(
            validate_image_upload(make_image("PNG"), "image/png").format,
            "PNG",
        )

    def test_empty_upload_is_rejected(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "empty"):
            validate_image_upload(b"", "image/jpeg")

    def test_oversized_upload_is_rejected(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "5 MB"):
            validate_image_upload(b"x" * (MAX_IMAGE_SIZE + 1), "image/jpeg")

    def test_unsupported_mime_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "Only JPEG and PNG"):
            validate_image_upload(make_image("JPEG"), "image/gif")

    def test_mime_signature_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ImageValidationError, "does not match"):
            validate_image_upload(make_image("JPEG"), "image/png")

    def test_corrupt_image_is_rejected(self) -> None:
        with self.assertRaises((OSError, SyntaxError, ValueError)):
            decode_image(b"\x89PNG\r\n\x1a\nnot-an-image")

    def test_successful_screening_is_explicitly_a_demo(self) -> None:
        result = DemoDiseaseAnalyzer().analyze(
            decode_image(make_image("JPEG"))
        )
        self.assertEqual(result.status, "screened")
        self.assertTrue(result.is_demo)
        self.assertEqual(result.certainty, "limited")
        self.assertIn("no disease classification", result.observation)
        self.assertIn("not a definitive", result.disclaimer)

    def test_small_image_returns_uncertain_result(self) -> None:
        result = DemoDiseaseAnalyzer().analyze(
            decode_image(make_image("PNG", size=(32, 32)))
        )
        self.assertEqual(result.status, "uncertain")
        self.assertEqual(result.observation, UNCERTAIN_MESSAGE)
        self.assertEqual(result.certainty, "none")
        self.assertTrue(result.is_demo)

    def test_response_contract_fields_are_present(self) -> None:
        result = DemoDiseaseAnalyzer().analyze(
            decode_image(make_image("PNG"))
        )
        self.assertEqual(
            set(result.__dataclass_fields__),
            {
                "status",
                "observation",
                "certainty",
                "next_step",
                "is_demo",
                "disclaimer",
            },
        )


if __name__ == "__main__":
    unittest.main()
