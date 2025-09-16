"""
Crypto & encoding helpers for Nemoria.

This module provides:
- Base64URL helpers without padding (`b64u_encode` / `b64u_decode`)
- Short unique ID generation (`uniqID`) using BLAKE2b over UUID+timestamp
- A simple, deterministic key derivation for Fernet (`pwd32`)
- JSON-(de)serialization with optional symmetric encryption (`encrypt`/`decrypt`)

Security notes:
- `pwd32` is **saltless** and fast; it's fine for demos/tests but for real
  security use a KDF with salt and work factor (e.g., PBKDF2/scrypt/argon2).
- `decrypt` raises `PermissionError("Invalid Password")` for *any* decode/
  decrypt/parse failure to avoid leaking details about the cause.
"""

from __future__ import annotations

import hashlib, base64, uuid, json, time
from cryptography.fernet import Fernet
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nemoria.protocol import JSON


__all__ = ("b64u_encode", "b64u_decode", "blake2b", "uniqID", "encrypt", "decrypt")


def b64u_encode(blob: bytes) -> str:
    """
    Encode raw bytes into a URL-safe Base64 string without padding.

    Args:
        blob: Input bytes.

    Returns:
        URL-safe Base64 string (with `=` padding removed).

    Example:
        >>> b64u_encode(b'hi')
        'aGk'
    """
    return base64.urlsafe_b64encode(blob).rstrip(b"=").decode("ascii")


def b64u_decode(string: str) -> bytes:
    """
    Decode a URL-safe Base64 string, accepting missing padding.

    Args:
        string: Base64-URL string (ASCII).

    Returns:
        Decoded raw bytes.

    Example:
        >>> b64u_decode('aGk') == b'hi'
        True
    """
    blob = string.encode("ascii")
    return base64.urlsafe_b64decode(blob + b"=" * (-len(blob) % 4))


def blake2b(string: str, length: int = 10) -> str:
    """
    Compute a BLAKE2b hash truncated to a fixed length (hex).

    Args:
        string: Input text to hash.
        length: Desired output length in hex characters (default 10).

    Returns:
        Hex digest string of exactly `length` characters.

    Notes:
        - Internally sets `digest_size` to cover the requested hex length.
    """
    ds = max(1, (length + 1) // 2)
    h = hashlib.blake2b(digest_size=ds)
    h.update(string.encode("utf-8"))
    return h.hexdigest()[:length]


def uniqID(length: int = 24) -> str:
    """
    Generate a short unique identifier (hex string).

    Combines a random UUID and the current timestamp (ns), then hashes
    them with BLAKE2b and truncates the hex digest.

    Args:
        length: Desired output length in hex characters (default 24).

    Returns:
        A unique ID string of length `length`.

    Note:
        Aimed at practicality and compactness; not a cryptographic nonce.
    """
    return blake2b(uuid.uuid4().hex + str(time.time_ns()), length)


def pwd32(pwd: str) -> str:
    """
    Derive a deterministic 32-byte Fernet key from a password.

    Steps:
        1) SHA-256 hash of the UTF-8 password → 32 bytes
        2) Base64-URL encode → Fernet-compatible key

    Args:
        pwd: Plain text password.

    Returns:
        Base64-URL string (ASCII) usable as a Fernet key.

    Warning:
        This is **saltless** and fast (deterministic). Prefer a real KDF
        (PBKDF2/scrypt/argon2) with a salt for production use.
    """
    digest = hashlib.sha256(pwd.encode("utf-8")).digest()  # 32 bytes
    return base64.urlsafe_b64encode(digest).decode("ascii")


def encrypt(obj: "JSON", pwd: Optional[str] = None) -> bytes:
    """
    Serialize a JSON object and optionally encrypt it (Fernet).

    Process:
        1) Serialize `obj` → UTF-8 JSON bytes
        2) Base64-URL encode → ASCII bytes
        3) If `pwd` is provided, encrypt with `Fernet(pwd32(pwd))`

    Args:
        obj: JSON-compatible object to serialize.
        pwd: Optional text password for encryption.

    Returns:
        - If no `pwd`: Base64-URL ASCII bytes of the JSON
        - If `pwd`: Fernet ciphertext bytes

    Raises:
        TypeError / ValueError: Propagated from `json.dumps` if `obj` is not serializable.
        Exception: Propagated from `Fernet.encrypt` on unexpected failures.

    Example:
        >>> encrypt({"k": 1})[:6] == b'eyJrIj'  # base64 of {"k":1}
        True
    """
    # 1) JSON → UTF-8 bytes (payload)
    json_bytes = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    # 2) Base64
    raw_b64_ascii = base64.urlsafe_b64encode(json_bytes)  # bytes (ASCII chars)

    if not pwd:
        return raw_b64_ascii

    key_ascii = pwd32(pwd).encode("ascii")
    return Fernet(key_ascii).encrypt(raw_b64_ascii)


def decrypt(blob: bytes, pwd: Optional[str] = None) -> "JSON":
    """
    Decrypt and deserialize a JSON object.

    Behavior:
        - If `pwd` is provided, attempts `Fernet(pwd32(pwd)).decrypt(blob)`.
        - Otherwise, treats `blob` as Base64-URL of the JSON bytes.
        - Decodes Base64, then parses JSON into a Python object.

    Args:
        blob: Data to decode (either raw base64 or Fernet ciphertext).
        pwd: Optional password to decrypt.

    Returns:
        Decoded JSON object.

    Raises:
        PermissionError: On any failure (wrong password, invalid token,
                         bad base64, decode, or JSON parse). Intentionally
                         generic to avoid leaking failure details.
    """
    try:
        data = blob if not pwd else Fernet(pwd32(pwd).encode("ascii")).decrypt(blob)
        json_bytes = base64.urlsafe_b64decode(data)
        return json.loads(json_bytes.decode("utf-8"))
    except Exception:
        raise PermissionError("Invalid Password") from None
