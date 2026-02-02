"""
Image compression utilities for CipherCanvas.
Uses lossless PNG compression so LSB-hidden data is preserved.
(JPEG is lossy and would destroy steganographic data.)
"""

from io import BytesIO

from PIL import Image


def compress_image(image: Image.Image, optimize: bool = True) -> bytes:
    """
    Compress image as PNG (lossless) and return as bytes.
    Preserves LSB-embedded data. optimize=True reduces file size.
    """
    buf = BytesIO()
    image.save(buf, format="PNG", optimize=optimize)
    buf.seek(0)
    return buf.read()


def decompress_image(data: bytes) -> Image.Image:
    """Load image from PNG bytes."""
    return Image.open(BytesIO(data)).convert("RGB")
