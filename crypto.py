# chacha20 + PBKDF2 for password-based encrypt/decrypt

from Crypto.Cipher import ChaCha20
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

NONCE_LEN = 8
KEY_LEN = 32
SALT_LEN = 16
PBKDF2_ITERATIONS = 100_000


def _derive_key(password: str, salt: bytes) -> bytes:
    return PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=KEY_LEN,
        count=PBKDF2_ITERATIONS,
    )


def encrypt(plaintext: str, password: str) -> bytes:
    # output: salt(16) + nonce(8) + ciphertext
    if not password:
        raise ValueError("Password is required for encryption")
    salt = get_random_bytes(SALT_LEN)
    key = _derive_key(password, salt)
    nonce = get_random_bytes(NONCE_LEN)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
    return salt + nonce + ciphertext


def decrypt(data: bytes, password: str) -> str:
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
