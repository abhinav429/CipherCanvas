# PNG only - lossless so LSB data stays intact

from io import BytesIO

from PIL import Image


def compress_image(image: Image.Image, optimize: bool = True) -> bytes:
    buf = BytesIO()
    image.save(buf, format="PNG", optimize=optimize)
    buf.seek(0)
    return buf.read()


def decompress_image(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data)).convert("RGB")
