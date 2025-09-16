"""
Timeout configuration for Nemoria components.

All values are in seconds. Any of them may be `None` to mean *wait indefinitely*.

- DEFAULT_TIMEOUT: default RPC/request timeout
- PING_TIMEOUT: round-trip budget for ping
- HANDSHAKE_TIMEOUT: deadline to complete the initial handshake
"""

from __future__ import annotations

from typing import Optional


__all__ = ("DEFAULT_TIMEOUT", "PING_TIMEOUT", "HANDSHAKE_TIMEOUT")


# Alias used across the codebase for clarity
TIMEOUT = Optional[float]

# All may be set to None (infinite wait)
DEFAULT_TIMEOUT: TIMEOUT = None
PING_TIMEOUT: TIMEOUT = 0.5
HANDSHAKE_TIMEOUT: TIMEOUT = 3
