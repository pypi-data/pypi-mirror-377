#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
Async client for a lightweight, in-memory data store over TCP.

This client opens a TCP connection, performs a handshake, sends framed
requests, and receives framed responses. It provides helpers for common
operations (GET/ALL/SET/DELETE/DROP/PURGE) and a latency probe (PING).

Concurrency model:
    A single socket (StreamReader/StreamWriter) is shared across requests.
    To avoid concurrent reads on the same StreamReader, requests are serialized
    via `self.lock`. Out-of-order frames that arrive while waiting for a
    specific reply are buffered in `self.inbox`.

Persistence note (SAVE):
    When invoked via convenience flags (e.g., `set(..., save=True)`), the client
    emits SAVE in a best-effort, fire-and-forget manner (it does NOT await an
    ACK). This prevents blocking on potentially long server-side I/O. If you
    need durability feedback, design an explicit ACK or later consistency probe.
"""

from __future__ import annotations

import asyncio, signal, time
from pyroute import Route
from collections import deque
from typing import Optional, Any, Union, Hashable, Dict, Literal, Deque
from nemoria.logger import logger
from nemoria.config import DEFAULT_TIMEOUT, PING_TIMEOUT, HANDSHAKE_TIMEOUT
from nemoria.protocol import Connection, Frame, Action, JSON
from nemoria.utils import send, recv


class Client:
    """
    Async client for the Nemoria store protocol.

    Responsibilities:
        - Open/close a TCP connection to the server.
        - Perform the initial handshake and keep peer metadata (`Connection`).
        - Send framed requests and await matching replies.
        - Provide helpers for GET/ALL/SET/DELETE/DROP/PURGE/PING and liveness checks.

    Concurrency model:
        Requests are serialized via `self.lock` so that a single request/response
        pair uses the socket at a time. This avoids concurrent reads on the same
        `StreamReader`. For high-throughput scenarios, consider a dedicated
        reader-task + pending-map architecture.

    SAVE semantics:
        The client may emit SAVE as a best-effort, non-blocking signal (no ACK
        awaited) when `save=True` is passed to convenience methods. This choice
        avoids blocking the event loop on disk I/O latency.
    """

    def __init__(
        self,
        host: Union[Literal["localhost", "127.0.0.1"], str] = "localhost",
        port: int = 8888,
        password: Optional[str] = None,
    ) -> None:
        """
        Initialize the client state (does not connect).

        Args:
            host: Server hostname or IP (e.g., "localhost", "127.0.0.1").
            port: Server TCP port.
            password: Optional shared secret.
        """
        self.host = host
        self.port = port
        self.password = password

        # Connection endpoints and context (populated by connect()).
        self.connection: Optional[Connection] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        # Buffer for out-of-order frames while waiting for a specific reply.
        # Size-limited to avoid unbounded growth.
        self.inbox: Deque[Frame] = deque(maxlen=1024)

        # Serialize request/response I/O over a single socket.
        self.lock = asyncio.Lock()

    async def connect(self) -> bool:
        """
        Open the TCP connection and complete the handshake.

        Behavior:
            - Establish a TCP connection to (host, port).
            - Perform a protocol handshake and read server `Connection` metadata.
            - Register best-effort signal handlers (SIGINT/SIGTERM) for clean close.
            - On failure, log the error and close any half-open resources.

        Returns:
            True on success, False otherwise.
        """
        try:
            # Establish connection.
            self.reader, self.writer = await asyncio.open_connection(
                self.host,
                self.port,
            )

            # Perform handshake and read server's connection metadata.
            if (connection_json := await self.handshake()) is None:
                raise ConnectionError
            self.connection = Connection.deserialize(
                connection_json, self.reader, self.writer
            )
            logger.info(f"{self.connection} SECURED.")

            # OS signal handlers → request a graceful close (best-effort).
            loop = asyncio.get_running_loop()
            try:
                loop.add_signal_handler(
                    signal.SIGINT, lambda: asyncio.create_task(self.close())
                )
                loop.add_signal_handler(
                    signal.SIGTERM, lambda: asyncio.create_task(self.close())
                )
            except NotImplementedError:
                # Some platforms (e.g., Windows) may not support this.
                pass

            # Success
            return True
        except ConnectionError:
            logger.error(f"Connection not established.")
        except Exception:
            logger.error(f"Connection to {(self.host, self.port)} FAILED.")
            # Ensure any half-open endpoints are closed.
            await self.close()

        # Failed
        return False

    async def close(self) -> None:
        """
        Close the client socket and release resources.

        Idempotent: safe to call multiple times. Logs on clean close.
        """
        if self.writer is not None:
            try:
                self.writer.close()
                try:
                    await self.writer.wait_closed()
                    logger.info(f"{self.connection or 'CLIENT'} CLOSED.")
                except Exception:
                    pass
            finally:
                self.writer = None
                self.reader = None

    async def shutdown(self) -> None:
        """
        Request a server-side shutdown (best-effort).

        Raises:
            ConnectionError: If not connected.
        """
        if self.reader is None or self.writer is None:
            raise ConnectionError("Connection not established.")
        await self._request(Frame(action=Action.SHUTDOWN))

    async def _send(self, frame: Frame) -> None:
        """
        Send a frame to the server.

        Args:
            frame: The frame to send.

        Raises:
            ConnectionError: If not connected.
        """
        if self.reader is None or self.writer is None:
            raise ConnectionError("Connection not established.")
        await send(self.writer, frame, self.password)

    async def _receive(self, reply_to: Optional[Frame] = None) -> Optional[Frame]:
        """
        Receive the next frame (optionally awaiting a matching reply).

        If `reply_to` is provided, unrelated frames are buffered in `inbox`
        until a frame with a matching `reply_to` arrives. This lets the client
        wait deterministically for the intended response without dropping other
        frames that may have arrived out of order.

        Args:
            reply_to: The originating request frame to match by `reply_to`.

        Returns:
            The received frame, or `None` if the connection was closed.

        Raises:
            ConnectionError: If not connected.
        """
        if self.reader is None or self.writer is None:
            raise ConnectionError("Connection not established.")

        while True:
            # Fast path: check buffered responses first.
            for frame in list(self.inbox):  # iterate over a snapshot
                if reply_to is not None and reply_to == frame.reply_to:
                    self.inbox.remove(frame)  # important: consume from inbox
                    return frame

            # Await a fresh frame from the wire.
            try:
                response = await recv(self.reader, self.password)
            except (
                EOFError,
                ConnectionError,
                ConnectionResetError,
                OSError,
                asyncio.IncompleteReadError,
            ):
                await self.close()
                return None

            # Protocol-level EOF/None → clean close.
            if response is None:
                await self.close()
                return None

            if reply_to is not None:
                if reply_to == response.reply_to:
                    return response
                # Buffer unrelated responses and continue waiting.
                self.inbox.append(response)
                continue

            # Not awaiting a specific reply; return what we got.
            return response

    async def _request(
        self, frame: Frame, timeout: Optional[float] = DEFAULT_TIMEOUT
    ) -> Optional[Frame]:
        """
        Send a request and await its corresponding response.

        Serialized by `self.lock` to avoid concurrent reads on the socket.

        Args:
            frame: The request frame to send.
            timeout: Optional timeout in seconds. If `None`, waits indefinitely.

        Returns:
            The matching response, or `None` on timeout/connection close.

        Raises:
            ConnectionError: If not connected.
        """
        if self.reader is None or self.writer is None:
            raise ConnectionError("Connection not established.")

        async with self.lock:
            # Transmit
            try:
                await self._send(frame)
            except (ConnectionError, ConnectionResetError, OSError) as e:
                logger.error(f"Connection error while sending: {e}")
                await self.close()
                return None

            # Await matching reply (or next frame if not specified)
            try:
                recv_coro = self._receive(reply_to=frame)
                return (
                    await asyncio.wait_for(recv_coro, timeout)
                    if timeout
                    else await recv_coro
                )
            except asyncio.TimeoutError:
                logger.error(f"Request timed out after {timeout:.2f}s")
                return None

    async def is_alive(self) -> bool:
        """
        Lightweight liveness check for the connection.

        Returns:
            True if endpoints are healthy and a PING round-trip succeeds;
            False otherwise.
        """
        if self.reader is None or self.writer is None:
            return False
        if self.reader.at_eof() or self.writer.is_closing():
            return False
        return (await self.ping()) is not None

    async def get(self, route: Route) -> Optional[Any]:
        """
        Fetch a value from the store.

        Args:
            route: The route/key to fetch.

        Returns:
            The value contained in the response frame (or `None` on failure).
        """
        frame = await self._request(Frame(action=Action.GET, route=route))
        return None if frame is None else frame.value

    async def all(self) -> Optional[Dict[Hashable, Any]]:
        """
        Fetch the entire store contents (server-defined semantics).
        """
        frame = await self._request(Frame(action=Action.ALL))
        return None if frame is None else frame.value

    async def set(self, route: Route, value: Any, save: bool = False) -> bool:
        """
        Set a value in the store.

        Args:
            route: The path/route to write.
            value: The value to store (must be protocol-serializable).
            save: If True, also trigger a SAVE operation to persist changes.

        Returns:
            True on ACK, False on timeout/error.
        """
        if (
            await self._request(Frame(action=Action.SET, route=route, value=value))
        ) is not None:
            if save:
                await self.save()
            return True
        return False

    async def delete(self, route: Route, save: bool = False) -> bool:
        """
        Delete a value from the store.

        Args:
            route: The path/route to remove.
            save: If True, also trigger a SAVE operation to persist changes.

        Returns:
            True on ACK, False on timeout/error.
        """
        if (await self._request(Frame(action=Action.DELETE, route=route))) is not None:
            if save:
                await self.save()
            return True
        return False

    async def drop(self, route: Route, save: bool = False) -> bool:
        """
        Drop the key at `route` entirely and prune empty ancestors upwards.

        Semantics:
            - Remove the target key itself (and its subtree, if any).
            - If any parent becomes empty, remove it too (recursive prune).

        Args:
            route: The path/route to remove.
            save: If True, also trigger a SAVE operation to persist changes.

        Returns:
            True on ACK, False on timeout/error.
        """
        if (await self._request(Frame(action=Action.DROP, route=route))) is not None:
            if save:
                await self.save()
            return True
        return False

    async def purge(self, save: bool = False) -> bool:
        """
        Clear all data in the store (destructive).

        Args:
            save: If True, also trigger a SAVE operation to persist changes.

        Returns:
            True on ACK, False on timeout/error.
        """
        if (await self._request(Frame(action=Action.PURGE))) is not None:
            if save:
                await self.save()
            return True
        return False

    async def save(self) -> None:
        """
        Trigger a SAVE operation on the server (fire-and-forget).

        Notes:
            - Sends a SAVE frame to the server but does not wait for any ACK.
            - Useful when persistence should be requested without blocking the client.
            - If you require confirmation that the data was written, use an explicit
            consistency check or design a server-side ACK.
        """
        await self._send(Frame(action=Action.SAVE))

    async def ping(self) -> Optional[float]:
        """
        Send PING and measure round-trip-time latency (RTT).

        Notes:
            This is a lightweight liveness probe. For throughput testing, prefer
            application-level benchmarks.

        Returns:
            Latency in milliseconds, or `None` on timeout/connection error.
        """
        start = time.perf_counter()
        if (await self._request(Frame(action=Action.PING), PING_TIMEOUT)) is None:
            return None
        rtt_ms = (time.perf_counter() - start) * 1000.0
        logger.info(f"{self.connection} PONG (RTT: {rtt_ms:.1f} ms).")
        return rtt_ms

    async def handshake(self) -> Optional[JSON]:
        """
        Perform a protocol handshake and return the server's connection info.

        Behavior:
            Sends a HANDSHAKE frame and expects a serialized `Connection` JSON
            in the reply. If the reply is missing or malformed, returns `None`.

        Returns:
            The server's serialized `Connection` JSON on success, otherwise `None`.
        """
        resp = await self._request(Frame(action=Action.HANDSHAKE), HANDSHAKE_TIMEOUT)
        return None if resp is None or resp.value is None else resp.value
