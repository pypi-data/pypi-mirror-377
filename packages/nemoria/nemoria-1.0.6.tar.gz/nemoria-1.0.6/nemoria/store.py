"""
Async-safe nested key-value store with a flat per-route lock map.

This module keeps application data (`db`) as nested dictionaries while
per-route locks are stored in a *flat* map keyed by the route object.
A meta-lock (`locks_guard`) serializes on-demand lock creation to prevent
races where concurrent tasks might create two different locks for the same
route.

Typical usage:
    store = Store(file="/path/to/state.json", file_format="JSON")
    await store.set(Route("users", "42", "name"), "Alice")
    name = await store.get(Route("users", "42", "name"))
    await store.delete(Route("users", "42"))      # collapses parent to None
    await store.drop(Route("users"))              # prunes empty ancestors
    await store.save()                            # async + atomic persistence

Persistence:
    Use `await store.save()` to persist `db` to disk. Saving is performed
    asynchronously using `aiofiles` and is atomic (temp → replace). The file
    file_format is either "JSON" or "YAML" (see `FORMATS`).
"""

from __future__ import annotations

import os
import json
import yaml
import asyncio
import aiofiles
import aiofiles.os as aios
from pyroute import Route
from typing import Optional, Any, Hashable, MutableMapping, Dict
from nemoria.logger import logger


FORMATS = ("JSON", "YAML")


class Store:
    """
    Task-safe nested store for asyncio workloads using a flat per-route lock map.

    Data:
        - `self.db`: nested dictionaries storing arbitrary values.
        - `self.locks`: flat map of per-route asyncio locks.
        - `self.locks_guard`: meta-lock that serializes lock creation so that
          concurrent tasks do not create duplicate locks for the same route.

    Notes:
        - `get()` returns `None` when the path is missing.
        - `set()` auto-creates intermediate dictionaries along the path.
        - `delete()` removes a subtree and, if the *immediate* parent becomes
          empty, replaces that parent with `None` (no recursive prune).
        - `drop()` removes the key and *recursively* prunes empty ancestors.
        - Locks are created lazily upon first use of a route.
    """

    def __init__(
        self,
        file: Optional[str] = None,
        file_format: Optional[str] = None,
    ) -> None:
        """
        Initialize empty data and lock maps.

        Creates:
            - `db`: the nested data dictionary.
            - `locks`: the flat lock dictionary (Route-keyed).
            - `locks_guard`: a meta-lock used only to serialize lock creation.

        Persistence:
            - `file` and `file_format` configure optional persistence. See `save()`.
        """
        self.file = file
        self.file_format = file_format

        self.db: Dict[Hashable, Any] = {}
        self.locks: Dict[Hashable, asyncio.Lock] = {}  # flat: Route (or key) -> Lock
        self.locks_guard = asyncio.Lock()  # guards lock creation

    async def lock(self, route: Route) -> asyncio.Lock:
        """
        Return the per-route lock for `route`, creating it if necessary.

        Fast path:
            Return an existing lock from `self.locks`.

        Slow path:
            Under `self.locks_guard`, create and memoize a new lock
            if one does not already exist.

        This method never raises due to lock lookup or creation.
        """
        # Fast path
        lock = self.locks.get(route)
        if lock is not None:
            return lock

        # Slow path: serialize creation to avoid duplicates
        async with self.locks_guard:
            return self.locks.setdefault(route, asyncio.Lock())

    async def get(self, route: Route) -> Optional[Any]:
        """
        Read and return the value at `route`, or `None` if missing.

        Concurrency:
            Acquires the per-route lock to serialize with concurrent writers.

        Args:
            route: Path to read.

        Returns:
            The stored value, or `None` if the path does not exist.
        """
        async with await self.lock(route):
            try:
                return await self._get(self.db, route)
            except KeyError:
                return None

    async def all(self) -> Dict[Hashable, Any]:
        """
        Return the internal data dictionary **by reference** (unsafe for mutation).

        Warning:
            This returns the live underlying dict. External code can mutate it
            without locking, bypassing `set()`/`delete()`. Prefer exposing a
            snapshot (`json.loads(json.dumps(self.db))`) if you need safety.

        Returns:
            The internal `db` dictionary (live reference).
        """
        return self.db

    async def set(self, route: Route, value: Any) -> None:
        """
        Write `value` at `route`, creating intermediate dictionaries as needed.

        Concurrency:
            Acquires the per-route lock before writing.

        Args:
            route: Destination path.
            value: Value to store.

        Errors:
            Exceptions from `_set()` (e.g., empty route or type mismatch) are
            swallowed here; consider logging or re-raising in production.
        """
        async with await self.lock(route):
            try:
                await self._set(self.db, route, value)
            except (ValueError, TypeError):
                logger.exception("store.set failed", exc_info=True)

    async def delete(self, route: Route) -> None:
        """
        Delete the subtree at `route`, collapsing only the immediate parent to `None` if empty.

        Semantics:
            - Remove the target subtree (key and descendants).
            - If the *immediate parent* becomes empty, replace that parent in its
              own parent with `None`.
            - No recursive pruning beyond the immediate parent.
            - Special case for top-level: `delete(["k"])` sets `db["k"] = None`.

        No-op if the path does not exist.
        """
        async with await self.lock(route):
            try:
                await self._delete(self.db, route, drop=False)
            except ValueError:
                logger.exception("store.delete failed", exc_info=True)

    async def drop(self, route: Route) -> None:
        """
        Drop the key at `route` and recursively prune empty ancestors.

        Semantics:
            - Remove the target key (and its subtree, if any).
            - If any parent becomes empty, remove it too (bottom-up).

        No-op if the path does not exist.
        """
        async with await self.lock(route):
            try:
                await self._delete(self.db, route, drop=True)
            except ValueError:
                logger.exception("store.drop failed", exc_info=True)

    async def purge(self) -> None:
        """
        Clear all data and all locks.

        Concurrency:
            Guarded by `locks_guard` to ensure a consistent full reset.
        """
        async with self.locks_guard:
            self.db.clear()
            self.locks.clear()

    async def save(self) -> None:
        """
        Persist `self.db` to disk and await completion.

        Notes:
            Uses atomic temp→replace semantics and non-blocking I/O under the hood.
        """
        async with self.locks_guard:
            asyncio.create_task(self._save(self.db, self.file, self.file_format))

    @staticmethod
    async def _get(obj: MutableMapping[Hashable, Any], route: Route) -> Any:
        """
        Traverse `obj` by `route` and return the value.

        Args:
            obj: Root mapping to traverse.
            route: Successive keys used to descend.

        Returns:
            Value at the end of the route.

        Raises:
            KeyError: If any segment is missing.
        """
        cur: Any = obj
        for seg in route:
            if isinstance(cur, MutableMapping) and seg in cur:
                cur = cur[seg]
            else:
                raise KeyError(seg)
        return cur

    @staticmethod
    async def _set(
        obj: MutableMapping[Hashable, Any],
        route: Route,
        value: Any,
    ) -> None:
        """
        Set `value` at `route` inside `obj`, creating parents as needed.

        Args:
            obj: Root mapping to modify.
            route: Path to set.
            value: Value to assign.

        Raises:
            ValueError: If `route` is empty.
            TypeError: If a non-mapping is encountered on the path.
        """
        if len(route) == 0:
            raise ValueError("route cannot be empty")

        cur: Any = obj
        for seg in route[:-1]:
            if not isinstance(cur, MutableMapping):
                raise TypeError(f"expected mapping at segment {seg!r}")
            if seg not in cur:
                cur[seg] = {}  # auto-create intermediate dict
            cur = cur[seg]

        if not isinstance(cur, MutableMapping):
            raise TypeError(f"expected mapping at final parent for {route[-1]!r}")
        cur[route[-1]] = value

    @staticmethod
    async def _delete(
        obj: MutableMapping[Hashable, Any],
        route: Route,
        drop: bool = False,
    ) -> None:
        """
        Core delete logic used by `delete()` and `drop()`.

        Modes:
            - drop=True  : remove key; prune empty parents bottom-up.
            - drop=False : remove subtree; if the immediate parent becomes empty,
                           replace that parent (in its own parent) with `None`.
                           Special-case: when len(route) == 1 -> obj[key] = None.

        Behavior:
            - Missing or malformed paths are silent no-ops.
            - Empty route raises ValueError.
            - Operates in-place on `obj`.
        """
        if len(route) == 0:
            raise ValueError("route cannot be empty")

        # Top-level special case for delete-mode
        if not drop and len(route) == 1:
            obj[route[0]] = None
            return

        # Walk to the parent of the target key
        cur: Any = obj
        parents: list[MutableMapping[Hashable, Any]] = []
        keys: list[Hashable] = []
        for seg in route[:-1]:
            if not isinstance(cur, MutableMapping) or seg not in cur:
                return  # no-op if path missing
            parents.append(cur)
            keys.append(seg)
            cur = cur[seg]

        if not isinstance(cur, MutableMapping):
            return  # malformed path → no-op

        target = route[-1]
        if target not in cur:
            return  # nothing to delete

        # Remove the target subtree (or leaf)
        cur.pop(target)

        if drop:
            # Prune empty parents bottom-up
            node = cur
            for gp, k in zip(reversed(parents), reversed(keys)):
                if isinstance(node, MutableMapping) and not node:
                    gp.pop(k, None)
                    node = gp
                else:
                    break
        else:
            # Collapse only the immediate parent to None if it became empty
            if not cur and parents:
                gp = parents[-1]
                key_of_parent = keys[-1]
                gp[key_of_parent] = None

    @staticmethod
    async def _save(
        obj: MutableMapping[Hashable, Any],
        file: Optional[str],
        file_format: Optional[str],
    ) -> None:
        """
        Asynchronously save a database object to a file in JSON or YAML format.

        Non-blocking I/O is done with `aiofiles`. The write is atomic:
        the payload is written to a temporary file which then replaces the
        target file via `replace()`. This minimizes the chance of partial writes.

        Args:
            obj: The mapping to serialize.
            file: Destination path (must be a non-empty string).
            file_format: "JSON" or "YAML" (see `FORMATS`).

        Notes:
            - If either `file` or `file_format` is falsy, the operation is aborted.
            - Invalid formats are logged as errors.
            - Serialization is done in memory first, then written asynchronously.
            - File I/O exceptions are logged but not re-raised.
        """
        if not file or not file_format:
            return

        fmt = file_format.strip().upper()

        # Ensure destination directory exists
        parent = os.path.dirname(os.path.abspath(file))
        if parent:
            try:
                await aios.makedirs(parent, exist_ok=True)
            except FileExistsError:
                pass

        # Serialize in memory
        if fmt == "JSON":
            payload = json.dumps(obj, indent=2, ensure_ascii=False)
        elif fmt == "YAML":
            payload = yaml.safe_dump(
                obj, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
        else:
            logger.error(f"Store.save error - INVALID FILE FORMAT ({file_format})")
            return

        # Write to a temp file, then atomically replace
        tmp_path = f"{file}.tmp.{os.getpid()}"

        try:
            async with aiofiles.open(
                tmp_path, "w", encoding="utf-8", newline="\n"
            ) as f:
                await f.write(payload)
                await f.flush()
            await aios.replace(tmp_path, file)
        except Exception as e:
            logger.error(f"Unexpected error while saving store: {e}")
            # Best-effort cleanup
            try:
                if await aios.path.exists(tmp_path):
                    await aios.remove(tmp_path)
            except Exception:
                pass
