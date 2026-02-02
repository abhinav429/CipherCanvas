"""
LSB (Least Significant Bit) steganography for CipherCanvas.
Hides and extracts raw bytes in the LSBs of image pixels.
Uses PNG-friendly representation; avoid lossy compression (e.g. JPEG) on stego-images.
"""

import struct
from io import BytesIO

import numpy as np
from PIL import Image


# Length prefix: 4 bytes (big-endian) = max payload ~4GB
LENGTH_PREFIX_BYTES = 4


def _image_to_array(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to RGB array (H, W, 3)."""
    img = img.convert("RGB")
    return np.array(img, dtype=np.uint8)


def _array_to_image(arr: np.ndarray) -> Image.Image:
    """Convert RGB array to PIL Image."""
    return Image.fromarray(arr.astype(np.uint8), mode="RGB")


def _bytes_to_bits(data: bytes) -> np.ndarray:
    """Convert bytes to flat array of bits (0 or 1), MSB first per byte."""
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    return bits


def _bits_to_bytes(bits: np.ndarray) -> bytes:
    """Convert flat array of bits to bytes (pad to multiple of 8)."""
    n = len(bits)
    pad = (8 - n % 8) % 8
    if pad:
        bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    return np.packbits(bits).tobytes()


def hide_in_image(image: Image.Image, data: bytes) -> Image.Image:
    """
    Hide raw bytes in the LSB of the image (RGB channels).
    First writes a 4-byte big-endian length, then the data.
    Returns a new PIL Image (RGB).
    """
    payload = struct.pack(">I", len(data)) + data
    bits = _bytes_to_bits(payload)
    num_bits = len(bits)

    arr = _image_to_array(image)
    h, w, c = arr.shape
    capacity_bits = h * w * c
    if num_bits > capacity_bits:
        raise ValueError(
            f"Data too large: {num_bits} bits needed, image has {capacity_bits} bits capacity"
        )

    # Flatten and overwrite LSBs
    flat = arr.reshape(-1)
    for i in range(num_bits):
        flat[i] = (flat[i] & 0xFE) | int(bits[i])
    return _array_to_image(arr)


def extract_from_image(image: Image.Image) -> bytes:
    """
    Extract bytes hidden by hide_in_image from the LSB of the image.
    """
    arr = _image_to_array(image)
    flat = arr.reshape(-1)

    # Read length prefix (4 bytes = 32 bits)
    length_bits = flat[: 8 * LENGTH_PREFIX_BYTES]
    bits = np.array([b & 1 for b in length_bits], dtype=np.uint8)
    length_bytes = _bits_to_bytes(bits)
    length = struct.unpack(">I", length_bytes[: LENGTH_PREFIX_BYTES])[0]

    total_bits = 8 * (LENGTH_PREFIX_BYTES + length)
    if total_bits > len(flat):
        raise ValueError("Image does not contain valid hidden data (length corrupted)")

    all_bits = np.array([b & 1 for b in flat[:total_bits]], dtype=np.uint8)
    all_bytes = _bits_to_bytes(all_bits)
    payload = all_bytes[: LENGTH_PREFIX_BYTES + length]
    return payload[LENGTH_PREFIX_BYTES:]


def open_image(file_or_path):
    """Open image from file object or path; return PIL Image."""
    if hasattr(file_or_path, "read"):
        img = Image.open(file_or_path)
    else:
        img = Image.open(file_or_path)
    return img.convert("RGB")
