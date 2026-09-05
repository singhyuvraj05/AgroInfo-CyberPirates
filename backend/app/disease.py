from dataclasses import dataclass
from io import BytesIO
from typing import Protocol

from PIL import Image


MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
}
UNCERTAIN_MESSAGE = "Unable to confidently screen this image."
DEMO_DISCLAIMER = (
    "Prototype screening only; not a definitive or scientifically validated "
    "disease diagnosis."
)


@dataclass(frozen=True)
class DiseaseScreeningResult:
    status: str
    observation: str
    certainty: str
    next_step: str
    is_demo: bool
    disclaimer: str


class ImageValidationError(ValueError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class DiseaseAnalyzer(Protocol):
    def analyze(self, image: Image.Image) -> DiseaseScreeningResult:
        """Analyze a decoded image without requiring a specific model."""


class DemoDiseaseAnalyzer:
    """A constrained image-quality screen, not a disease classifier."""

    def analyze(self, image: Image.Image) -> DiseaseScreeningResult:
        if image.width < 64 or image.height < 64:
            return DiseaseScreeningResult(
                status="uncertain",
                observation=UNCERTAIN_MESSAGE,
                certainty="none",
                next_step=(
                    "Upload a clear, well-lit close-up of the affected leaf "
                    "or seek local agricultural expert advice."
                ),
                is_demo=True,
                disclaimer=DEMO_DISCLAIMER,
            )

        return DiseaseScreeningResult(
            status="screened",
            observation=(
                "Image accepted for constrained prototype screening; no "
                "disease classification was performed."
            ),
            certainty="limited",
            next_step=(
                "Use this result only as a demo workflow. Inspect the plant "
                "carefully and consult a local agricultural expert before "
                "taking treatment action."
            ),
            is_demo=True,
            disclaimer=DEMO_DISCLAIMER,
        )


def decode_image(image_bytes: bytes) -> Image.Image:
    image = Image.open(BytesIO(image_bytes))
    image.verify()
    decoded = Image.open(BytesIO(image_bytes))
    decoded.load()
    return decoded


def validate_image_upload(image_bytes: bytes, content_type: str | None) -> Image.Image:
    signature = ALLOWED_IMAGE_TYPES.get(content_type or "")
    if signature is None:
        raise ImageValidationError(
            415,
            "Only JPEG and PNG images are supported",
        )
    if not image_bytes:
        raise ImageValidationError(400, "The uploaded image is empty")
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ImageValidationError(413, "The image exceeds the 5 MB limit")
    if not image_bytes.startswith(signature):
        raise ImageValidationError(
            415,
            "The image MIME type does not match its file signature",
        )
    try:
        return decode_image(image_bytes)
    except (OSError, SyntaxError, ValueError) as error:
        raise ImageValidationError(
            422,
            "The uploaded image is corrupt or cannot be decoded",
        ) from error
