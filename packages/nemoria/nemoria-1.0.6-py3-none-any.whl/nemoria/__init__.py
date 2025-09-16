"""
Nemoria: Lightweight Async In-Memory Data Store
===============================================

Nemoria is a lightweight, asynchronous, in-memory datastore with a simple
client-server architecture. It is designed for fast experiments, prototyping,
and educational use cases where a minimal and hackable data layer is needed.

Core Components:
----------------
- **Server**:
  An asynchronous TCP server that accepts client connections, authenticates
  via password, and handles CRUD-style operations on nested routes.

- **Client**:
  A high-level asynchronous client for connecting to the server, performing
  set/get/delete/drop operations, and traversing stored data.

- **Route**:
  A helper class for representing nested keys (paths) in the datastore, making
  it easy to organize hierarchical data structures.

Features:
---------
- Asynchronous I/O with `asyncio`
- Password-based authentication
- Nested routes for structured data
- Simple CRUD interface (create, read, update, delete)
- Minimalistic and extensible design

Quick Example:
--------------
    from nemoria import Client, Route

    async def demo():
        client = Client(host="localhost", port=1234, password="12345678")
        await client.connect()
        await client.set(Route("foo", "bar"), "baz")
        print(await client.all())
"""

from .server import Server
from .client import Client
from pyroute import Route

__all__ = ("Server", "Client", "Route")
__version__ = "1.0.6"
