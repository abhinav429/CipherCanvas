"""
ChaCha20 encryption/decryption for CipherCanvas.
Uses PBKDF2 for key derivation from password; ChaCha20 for symmetric encryption.
"""

import os
from base64 import b64encode, b64decode

from Crypto.Cipher import ChaCha20
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# ChaCha20 key is 32 bytes; nonce 8 bytes (ChaCha20) or 12 (ChaCha20-Poly1305)
NONCE_LEN = 8
KEY_LEN = 32
SALT_LEN = 16
PBKDF2_ITERATIONS = 100_000


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from password using PBKDF2."""
    return PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=KEY_LEN,
        count=PBKDF2_ITERATIONS,
    )


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt plaintext with ChaCha20 using a password-derived key.
    Returns: salt (16) + nonce (8) + ciphertext (variable).
    """
    if not password:
        raise ValueError("Password is required for encryption")
    salt = get_random_bytes(SALT_LEN)
    key = _derive_key(password, salt)
    nonce = get_random_bytes(NONCE_LEN)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
    return salt + nonce + ciphertext


def decrypt(data: bytes, password: str) -> str:
    """
    Decrypt data produced by encrypt().
    Expects: salt (16) + nonce (8) + ciphertext.
    """
    if not password:
        raise ValueError("Password is required for decryption")
    if len(data) < SALT_LEN + NONCE_LEN:
        raise ValueError("Invalid ciphertext (too short)")
    salt = data[:SALT_LEN]
    nonce = data[SALT_LEN : SALT_LEN + NONCE_LEN]
    ciphertext = data[SALT_LEN + NONCE_LEN :]
    key = _derive_key(password, salt)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode("utf-8")
