import base64
from PIL import Image, ImageEnhance
from io import BytesIO
from dataclasses import dataclass


@dataclass
class WatermarkSettings:
    """
    Settings used to define how the watermark is applied
    Parameters:
        alpha: Defines the opacity of the image used as a watermark. Can be any value between 0-1 with 0 meaning not visible at all and 1 meaning not transparent at all
        rotation: Defines the rotation applied to the watermark in degrees (e.g. 90 instead of Math.PI/2)
        scale: Defines how much the image should be scaled before being added as a watermark
    """
    alpha: float = 0.45
    rotation: float = 30
    scale: float = 0.3


def tile_image(base_image, tile_image, alpha=1.0, rotation=0, scale=1.0):
    """
    Draws the second image in a repeating pattern over the first image with configurable alpha, rotation, and scale.

    :param base_image: PIL.Image object for the base canvas.
    :param tile_image: PIL.Image object for the tile.
    :param alpha: Transparency of the tile image (0.0 to 1.0).
    :param rotation: Rotation angle in degrees for the tile image.
    :param scale: Scale factor for resizing the tile image.
    :return: A new PIL.Image object with the pattern applied.
    """
    # Ensure alpha is within valid bounds
    alpha = max(0.0, min(1.0, alpha))
    
    # Resize and rotate the tile image
    original_width, original_height = tile_image.size
    new_width = max(1, int(original_width * scale))
    new_height = max(1, int(original_height * scale))
    resized_tile = tile_image.resize((new_width, new_height), Image.LANCZOS).rotate(rotation, expand=True)

    # Apply alpha transparency
    if resized_tile.mode != 'RGBA':
        resized_tile = resized_tile.convert('RGBA')
    alpha_layer = ImageEnhance.Brightness(resized_tile.split()[3]).enhance(alpha)
    resized_tile.putalpha(alpha_layer)

    # Create a new image for tiling
    base_width, base_height = base_image.size
    tiled_image = base_image.convert('RGBA')
    tile_width, tile_height = resized_tile.size

    # Paste the tile image repeatedly, add a small buffer so the tiling effect looks better
    for x in range(0, base_width, int(tile_width*1.1)):
        for y in range(0, base_height, int(tile_height*1.1)):
            tiled_image.paste(resized_tile, (x, y), resized_tile)

    return tiled_image


def add_image_watermark(base_image, watermark_image, watermark_settings):
    """
    Adds an image watermark to another image.

    Parameters:
        base_image (PIL.Image): The main image to which the watermark will be added.
        watermark_image (PIL.Image): The image to be used as a watermark
        watermark_settings (pypixelamrk.WatermarkSettings): Settings defining how the watermark is applied
    """
    # Converting to RGBA to ensure we can apply opacity
    watermark_image = watermark_image.convert("RGBA")
    result = tile_image(base_image, watermark_image, alpha=watermark_settings.alpha, rotation=watermark_settings.rotation, scale=watermark_settings.scale)

    return result


def pil_image_to_base64(base_image:Image, watermark_image:Image, watermark_settings=None, watermark=True, format='JPEG'):
    """
    Generates a base64 encoded string from a PIL image that can be used as a data element in HTML content

    Parameters:
        image (PIL.Image): The image that needs to be encoded and watermarked if necessary
        watermark_image(PIL.Image): The image to be used as a watermark. If None the funciton behaves as if watermark is False
        watermark (Boolean): Whether to add a watermark to base image or not
        watermark_settings (pypixelmark.WatermarkSettings): Settings defining how the watermark is applied. If None the default settings of {scale: 0.3, alpha: 0.45, rotation: 30} will be applied 
        format: The format the image is saved as, same as the format parameter in PIL.Image.save

    :raises ValueError: If the base_image is not a PIL.Image or is None       
    """
    # Convert the PIL image to bytes
    result = base_image
    settings = watermark_settings

    if base_image is None:
        raise ValueError(f'A PIL.Image instance is required as base_image for the encoding process, but {type(base_image)} found')

    if settings is None:
        settings = WatermarkSettings()

    if watermark and watermark_image is not None:
        result = add_image_watermark(base_image, watermark_image, watermark_settings=settings)
    buffered = BytesIO()
    result.convert('RGB').save(buffered, format=format)
    
    # Encode the bytes to base64
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Format the base64 string as a data URL for HTML
    mime_type = f"image/{format.lower()}"
    base64_data = f"data:{mime_type};base64,{img_str}"
    
    return base64_data
