# CipherCanvas

**Secure Image-Based Hiding Using Steganography**

CipherCanvas encrypts a secret message with ChaCha20, hides it inside an image using LSB steganography, and returns a compressed (lossless PNG) stego-image. Only someone with the same password can extract and decrypt the message.

## Features

- **Secure** — Messages are encrypted with ChaCha20 (PyCryptodome), with keys derived via PBKDF2.
- **Image-based hiding** — The carrier is an image; pixel LSBs are subtly modified to embed data.
- **Steganography** — Presence of hidden data is not obvious from the image.
- **Compression** — Stego-images are saved as optimized PNG (lossless) for smaller size while preserving hidden data.

## Tech stack

- Python 3
- Flask (backend API)
- Pillow (image handling, PNG compression)
- NumPy (pixel manipulation for LSB)
- PyCryptodome (ChaCha20 + PBKDF2)

## Setup

```bash
cd /path/to/Cryptography
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## Usage

1. **Hide Message** — Upload a carrier image, enter your secret message and a password. Click “Hide Message” to download a stego-image (PNG).
2. **Reveal Message** — Upload a stego-image created with CipherCanvas and enter the same password. The decrypted message is shown.

## Project layout

- `app.py` — Flask app and `/api/hide`, `/api/reveal` endpoints
- `crypto.py` — ChaCha20 encrypt/decrypt and PBKDF2 key derivation
- `steganography.py` — LSB hide/extract in images
- `compression.py` — PNG (lossless) compression for stego-images
- `templates/` — HTML frontend
- `static/` — CSS and JS

## Note on format

Stego-images are always PNG. JPEG is not used for output because it is lossy and would destroy the LSB-embedded data.
