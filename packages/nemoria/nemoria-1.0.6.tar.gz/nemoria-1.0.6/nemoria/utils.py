"""
Framed I/O utilities for the Nemoria protocol.

Messages are sent and received as **length-prefixed** binary frames:
- A 4-byte **big-endian** unsigned integer header specifies payload length.
- The payload is optionally **encrypted** (using `pwd`) and must decode to a
  Python `dict` that `Frame.deserialize()` can consume.

These helpers do not catch network/crypto errors beyond basic validation; such
errors are allowed to propagate so callers can decide how to handle them.
"""

from __future__ import annotations

import asyncio
import socket
from typing import Optional
from nemoria.cryptography import encrypt, decrypt
from nemoria.protocol import Frame


__all__ = ("recv", "send", "validate_addr")


async def recv(reader: asyncio.StreamReader, pwd: Optional[str] = None) -> Frame:
    """
    Read one length-prefixed frame and return a `Frame` instance.

    This function:
      1) reads a 4-byte big-endian length header,
      2) reads exactly `length` bytes of payload,
      3) decrypts (if `pwd` is provided) and deserializes the payload into a `Frame`.

    Args:
        reader: The stream to read from (bound to a TCP socket).
        pwd: Optional shared secret used by `decrypt()`.

    Returns:
        A `Frame` reconstructed via `Frame.deserialize(...)`.

    Raises:
        asyncio.IncompleteReadError: If the stream closes before enough bytes arrive.
        ValueError: If the length is non-positive or the decrypted payload is not a dict.
        Exception: Any error raised by `decrypt()` or `Frame.deserialize()` is propagated.

    Notes:
        - This call is **framing-aware** and blocks until a full frame is available.
        - It does not perform retries; callers should handle reconnection/backoff.
    """
    # Read 4-byte header: payload length (big-endian)
    hdr = await reader.readexactly(4)
    length = int.from_bytes(hdr, "big")
    if length <= 0:
        raise ValueError("invalid frame length")

    # Read payload and decode -> dict
    payload = await reader.readexactly(length)
    doc = decrypt(payload, pwd)
    if not isinstance(doc, dict):
        raise ValueError("invalid frame payload (expected dict)")

    return Frame.deserialize(doc)


async def send(
    writer: asyncio.StreamWriter, frame: Frame, pwd: Optional[str] = None
) -> None:
    """
    Serialize, (optionally) encrypt, and send a single framed message.

    The message is serialized via `Frame.serialize()`, encrypted with `encrypt()`
    when `pwd` is provided, and written as:
        [4-byte big-endian length][payload-bytes]

    Args:
        writer: The stream to write to (bound to a TCP socket).
        frame: The `Frame` to serialize and send.
        pwd: Optional shared secret used by `encrypt()`.

    Raises:
        ConnectionError, ConnectionResetError, BrokenPipeError: On I/O failures.
        Exception: Any error raised by `encrypt()` or `frame.serialize()` is propagated.

    Notes:
        - `await writer.drain()` applies backpressure; this may block under load.
        - No internal buffering beyond the framing header is performed here.
    """
    # Serialize & encrypt to raw bytes
    payload = encrypt(frame.serialize(), pwd)
    # Write header + payload, then flush
    writer.write(len(payload).to_bytes(4, "big") + payload)
    await writer.drain()


async def validate_addr(host: str, port: int) -> bool:
    """
    Resolve a host/port pair to check basic TCP address validity.

    This performs an asynchronous `getaddrinfo()` lookup to verify that the
    host and port are syntactically valid and resolvable on the current system.
    It does **not** bind or open a socket.

    Args:
        host: Hostname or IP address to validate.
        port: TCP port number to validate.

    Returns:
        True if resolution succeeds; False otherwise (errors are swallowed).

    Examples:
        >>> await validate_addr("localhost", 8888)
        True
        >>> await validate_addr("256.256.256.256", 1234)
        False
    """
    try:
        loop = asyncio.get_running_loop()
        await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except Exception:
        return False
    return True
