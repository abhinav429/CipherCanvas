# LSB stego - hide bytes in image LSBs, extract same. use PNG only (jpeg kills it)

import struct
from io import BytesIO

import numpy as np
from PIL import Image

LENGTH_PREFIX_BYTES = 4  # big-endian uint32 for payload length


def _image_to_array(img: Image.Image) -> np.ndarray:
    img = img.convert("RGB")
    return np.array(img, dtype=np.uint8)


def _array_to_image(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8), mode="RGB")


def _bytes_to_bits(data: bytes) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    return bits


def _bits_to_bytes(bits: np.ndarray) -> bytes:
    n = len(bits)
    pad = (8 - n % 8) % 8
    if pad:
        bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    return np.packbits(bits).tobytes()


def hide_in_image(image: Image.Image, data: bytes) -> Image.Image:
    # payload = 4-byte length (big-endian) + data
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

    flat = arr.reshape(-1)
    for i in range(num_bits):
        flat[i] = (flat[i] & 0xFE) | int(bits[i])
    return _array_to_image(arr)


def extract_from_image(image: Image.Image) -> bytes:
    arr = _image_to_array(image)
    flat = arr.reshape(-1)
    # first 32 bits = length
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
    if hasattr(file_or_path, "read"):
        img = Image.open(file_or_path)
    else:
        img = Image.open(file_or_path)
    return img.convert("RGB")
