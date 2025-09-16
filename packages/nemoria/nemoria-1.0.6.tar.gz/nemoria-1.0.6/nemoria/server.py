"""
Async TCP server for a lightweight in-memory data store.

This module exposes `Server`, which accepts client connections, performs a
handshake, receives framed requests, dispatches them to handlers, and sends
framed responses. It also provides graceful shutdown on OS signals or via
a client request.
"""

from __future__ import annotations

import asyncio
import signal
import contextlib
from typing import Optional, Union, Literal, Set
from errno import EADDRINUSE, EACCES, EADDRNOTAVAIL
from nemoria.logger import logger
from nemoria.config import HANDSHAKE_TIMEOUT
from nemoria.protocol import Connection, Frame, Action
from nemoria.store import Store
from nemoria.cryptography import uniqID
from nemoria.utils import send, recv, validate_addr


class Server:
    """
    Async TCP server for a lightweight in-memory data store.

    Responsibilities:
        • Accept client connections and perform a simple handshake
        • Receive frames and route them to `dispatch`
        • Send responses back to clients
        • Gracefully shut down on OS signals or programmatic request

    Notes:
        Subclass and override `dispatch` to implement your protocol (CRUD,
        pub/sub, queries, etc.). The default implementation covers a minimal
        request set for a key-value store.
    """

    def __init__(
        self,
        host: Union[Literal["localhost", "127.0.0.1"], str] = "localhost",
        port: int = 8888,
        namespace: str = "Nemoria",
        password: Optional[str] = None,
        file: Optional[str] = None,
        file_format: Optional[Literal["JSON", "YAML"]] = None,
    ) -> None:
        """
        Initialize server state (does not bind or listen yet).

        Args:
            host: Address to bind to (e.g., "localhost" or "127.0.0.1").
            port: TCP port to listen on.
            namespace: Name used in logs to distinguish instances.
            password: Optional shared secret used by the protocol.
            file: Destination path. (e.g. "output.json")
            file_format: "JSON" or "YAML" (see `FORMATS`).
        """
        self.host = host
        self.port = port
        self.namespace = namespace
        self.password = password

        # Listener + active connections
        self.server: Optional[asyncio.AbstractServer] = None
        self.connections: Set[Connection] = set()

        # Application data store (customize/replace as needed)
        self.store = Store(file=file, file_format=file_format)

    async def run_forever(self, raise_on_error: bool = True) -> None:
        """
        Bind, listen, and serve until cancelled or shutdown is requested.

        Installs SIGINT/SIGTERM handlers (when supported) that trigger a
        graceful shutdown. Common bind errors are logged with helpful messages.

        Args:
            raise_on_error:
                If True, any error encountered during bind or serve will be
                re-raised to the caller *after* graceful shutdown is performed.
                If False, errors will be logged but swallowed.
        """
        exc: Optional[BaseException] = None  # store error to re-raise later

        try:
            # Validate host:port before binding
            if not await validate_addr(self.host, self.port):
                raise OSError(EADDRNOTAVAIL, "address not available")

            # Create the asyncio server and bind the socket
            self.server = await asyncio.start_server(
                self.handle_connection, self.host, self.port
            )

            # Register OS signal handlers for graceful shutdown
            loop = asyncio.get_running_loop()
            try:
                loop.add_signal_handler(
                    signal.SIGINT, lambda: asyncio.create_task(self.shutdown())
                )
                loop.add_signal_handler(
                    signal.SIGTERM, lambda: asyncio.create_task(self.shutdown())
                )
            except NotImplementedError:
                # Some platforms (e.g., Windows) do not support signals
                pass

            # Run server until cancelled
            async with self.server:
                logger.info(f"[{self.namespace}] LISTENING ON {(self.host, self.port)}")
                await self.server.serve_forever()

        except asyncio.CancelledError:
            # Normal cancellation (Ctrl+C, shutdown requested) → ignore
            pass

        except OSError as e:
            # Categorize common bind failures
            if e.errno == EADDRINUSE:
                logger.error(
                    f"[{self.namespace}] address in use: {(self.host, self.port)}"
                )
            elif e.errno == EACCES:
                logger.error(
                    f"[{self.namespace}] permission denied for {(self.host, self.port)} "
                    "(try a higher port or elevated privileges)"
                )
            elif e.errno == EADDRNOTAVAIL:
                logger.error(
                    f"[{self.namespace}] address not available: {(self.host, self.port)}"
                )
            else:
                logger.error(
                    f"[{self.namespace}] OS error on bind {(self.host, self.port)}: {e!r}"
                )
            exc = e

        except Exception as e:
            # Any other unexpected error
            logger.exception(
                f"[{self.namespace}] unexpected error on {(self.host, self.port)}"
            )
            exc = e

        finally:
            # Always shutdown server gracefully
            await self.shutdown()

            # Optionally propagate the error upward
            if raise_on_error and exc is not None:
                raise exc

    async def shutdown(self) -> None:
        """
        Gracefully close the server and all active client connections.

        This is the single place where shutdown is performed.
        Safe to call multiple times (idempotent).
        """
        # Close all client connections (create a snapshot to avoid mutation during iteration)
        for connection in {*self.connections}:
            await self.close_connection(connection)

        # Close the listening server
        if self.server is not None:
            self.server.close()
            with contextlib.suppress(Exception):
                await self.server.wait_closed()
            self.server = None

        logger.info(f"[{self.namespace}] SERVER SHUTDOWN.")

    async def dispatch(self, connection: Connection, frame: Frame) -> None:
        """
        Route an incoming frame to the appropriate handler.

        Override this method to implement application logic (CRUD, pub/sub,
        query execution, etc.). The default behavior includes ACKs for
        mutating operations to let clients correlate completion.

        Args:
            connection: The client connection context.
            frame: The decoded frame from the client.
        """
        match frame.action:
            case Action.GET:
                result = None
                if frame.route is not None:
                    result = await self.store.get(frame.route)
                await send(
                    connection.writer,
                    Frame(value=result, reply_to=frame),
                    self.password,
                )

            case Action.ALL:
                result = await self.store.all()
                await send(
                    connection.writer,
                    Frame(value=result, reply_to=frame),
                    self.password,
                )

            case Action.SET:
                if frame.route is not None:
                    await self.store.set(frame.route, frame.value)
                # ACK
                await send(connection.writer, Frame(reply_to=frame), self.password)

            case Action.DELETE:
                if frame.route is not None:
                    await self.store.delete(frame.route)
                # ACK
                await send(connection.writer, Frame(reply_to=frame), self.password)

            case Action.DROP:
                if frame.route is not None:
                    await self.store.drop(frame.route)
                # ACK
                await send(connection.writer, Frame(reply_to=frame), self.password)

            case Action.PURGE:
                await self.store.purge()
                # ACK
                await send(connection.writer, Frame(reply_to=frame), self.password)

            case Action.SAVE:
                await self.store.save()

            case Action.PING:
                await send(connection.writer, Frame(reply_to=frame), self.password)
                logger.info(f"[{self.namespace}] {connection} PING.")

            case Action.HANDSHAKE:
                await send(
                    connection.writer,
                    Frame(
                        value=connection.serialize(),
                        reply_to=frame,
                    ),
                    self.password,
                )
                logger.info(f"[{self.namespace}] {connection} HANDSHAKE.")

            case Action.SHUTDOWN:
                # Request server stop; run_forever.finally() performs the cleanup.
                # Send ACK before closing to ensure the client is unblocked.
                await send(connection.writer, Frame(reply_to=frame), self.password)
                if self.server is not None:
                    self.server.close()
                    return

    async def handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Accept a new client, perform handshake, then process frames.

        The connection is registered only after a valid handshake.
        Frames are read in a loop and routed to `dispatch`; the connection is
        always deregistered and closed in the `finally` block.

        Args:
            reader: Stream reader bound to the client socket.
            writer: Stream writer bound to the client socket.
        """
        # Identify peer (best-effort; shape of `peername` can vary by platform)
        peer = writer.get_extra_info("peername")
        if peer is None:
            host, port = "unknown", 0
        else:
            try:
                host, port = peer[0], peer[1]
            except Exception:
                host, port = "unknown", 0

        connection = Connection(uniqID(8), host, port, reader, writer)

        try:
            # 1) Handshake (with timeout)
            handshake = await asyncio.wait_for(
                recv(reader, self.password), HANDSHAKE_TIMEOUT
            )
            if handshake.action != Action.HANDSHAKE:
                raise PermissionError
            await self.dispatch(connection, handshake)

            # 2) Activate connection after successful handshake
            self.connections.add(connection)

            # 3) Main receive loop
            while True:
                frame = await recv(reader, self.password)
                if frame is None:
                    break
                # Dispatch asynchronously to avoid head-of-line blocking.
                # If your protocol requires strict per-connection ordering,
                # serialize dispatches instead of creating tasks.
                asyncio.create_task(self.dispatch(connection, frame))

        except asyncio.CancelledError:
            # Bubble up: run_forever handles the global shutdown path
            raise asyncio.CancelledError

        except asyncio.TimeoutError:
            logger.error(f"[{self.namespace}] {connection} REFUSED.")

        except PermissionError:
            logger.error(f"[{self.namespace}] {connection} UNAUTHORIZED.")

        except EOFError:
            logger.error(f"[{self.namespace}] {connection} CLOSED.")

        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            logger.error(f"[{self.namespace}] {connection} LOST.")

        finally:
            await self.close_connection(connection)

    async def close_connection(self, connection: Connection) -> None:
        """
        Close a single client connection and remove it from the registry.

        Idempotent: safe to call multiple times.
        """
        writer = connection.writer
        if writer.is_closing():
            with contextlib.suppress(Exception):
                await writer.wait_closed()
        else:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()
        self.connections.discard(connection)
