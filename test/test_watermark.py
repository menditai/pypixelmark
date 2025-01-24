
import pytest
import random

from PIL import Image, ImageChops
from pypixelwatermark import WatermarkSettings, pil_image_to_base64


def generate_random_image(width, height):
    
    # Image generated as an array with dimensions [height, width, channel] where channel represents red, green and blue
    imarray = [[[random.randint(0, 255) for c in range(3)] for x in range(width)] for y in range(height)]
    imarray = bytes([c for y in imarray for x in y for c in x])
    im = Image.frombytes("RGB", (width, height), imarray)
    return im


# Ensures a default settings instance can always be created, only expected to fail if an error is raised
def test_settings_class_initialization():
    instance = WatermarkSettings()
    assert(instance is not None)


def test_none_base_image():
    with pytest.raises(ValueError):
        pil_image_to_base64(None, None)


def test_no_watermark_image():
    base_image = generate_random_image(10, 10)
    watermark_image = generate_random_image(2, 2)
    resultA = pil_image_to_base64(base_image, None)
    resultB = pil_image_to_base64(base_image, None, watermark=False)
    assert(resultA == resultB), "Different base image content detected when no watermark was provided"


def test_watermark_is_added():
    base_image = generate_random_image(10, 10)
    watermark_image = generate_random_image(2, 2)
    result_watermarked = pil_image_to_base64(base_image, watermark_image)
    result_base = pil_image_to_base64(base_image, None)

    assert(result_watermarked != result_base), "No watermark applied even though a watermark image was provided"


def test_valid_content_encoding():
    base_image = generate_random_image(10, 10)

    result_png = pil_image_to_base64(base_image, None, format="PNG")
    result_jpeg = pil_image_to_base64(base_image, None, format="JPEG")
    
    assert(result_png.startswith("data:image/png;base64,"))
    assert(result_jpeg.startswith("data:image/jpeg;base64,"))