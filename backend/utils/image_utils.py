from io import BytesIO
from PIL import Image
from typing import BinaryIO

MAX_IMAGE_DIMENSION = 1024
SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB


def validate_image_bytes(image_bytes: bytes) -> None:
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Image exceeds the 8 MB file size limit.")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            if image.format is None or image.format.upper() not in SUPPORTED_FORMATS:
                raise ValueError("Unsupported image format. Allowed types: JPG, JPEG, PNG, WEBP.")
    except Exception as exc:
        raise ValueError("Unable to read the uploaded image. Please upload a valid image file.") from exc


def load_and_resize_image(image_bytes: bytes) -> Image.Image:
    with Image.open(BytesIO(image_bytes)) as image:
        image = image.convert("RGB")
        width, height = image.size
        if max(width, height) > MAX_IMAGE_DIMENSION:
            scale = MAX_IMAGE_DIMENSION / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.LANCZOS)
        return image.copy()
