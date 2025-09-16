from __future__ import annotations

import asyncio
import dataclasses
import importlib
import inspect
import cloudpickle as pickle
from datetime import date, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from multiprocessing.synchronize import Lock as LockClass

    from wombat.multiprocessing.ipc.queues.trait_queue import TraitQueue


def _resolve_path(path: str) -> Any:
    """Dynamically imports an object from a string path."""
    try:
        module_name, obj_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, obj_name)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Could not import object from path: {path}") from e


def default_encoder(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if inspect.isclass(obj):
        return {"__pickle__": True, "data": pickle.dumps(obj)}
    if callable(obj) and inspect.isfunction(obj):
        if obj.__name__ == "<lambda>":
            raise TypeError("Lambda functions are not serializable")
        if "<locals>" in obj.__qualname__:
            raise TypeError("Nested functions are not serializable")
        # Functions defined in tests or `__main__` are not importable by name
        # in spawned worker processes. We must pickle them to transfer them.
        if obj.__module__ == "__main__" or obj.__module__.startswith("tests"):
            return {"__pickle__": True, "data": pickle.dumps(obj)}
        return f"{obj.__module__}.{obj.__name__}"
    raise TypeError(f"Object of type {type(obj).__name__} is not serializable")


def is_async_context_manager(obj):
    return hasattr(obj, "__aenter__") and hasattr(obj, "__aexit__")


def is_sync_context_manager(obj):
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")


class AsyncProcessLock:
    """An async-compatible wrapper around a multiprocessing.Lock."""

    def __init__(self, lock: "LockClass", loop: "asyncio.AbstractEventLoop"):
        self._lock = lock
        self._loop = loop

    async def acquire(self):
        """
        Asynchronously acquire the lock by running the blocking call in an executor.
        Shielded to prevent cancellation while waiting for the lock, which could
        lead to a leaked lock and deadlock.
        """
        await asyncio.shield(self._loop.run_in_executor(None, self._lock.acquire))

    async def release(self):
        """Release the lock."""
        self._lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


async def queue_get_async(queue: "TraitQueue") -> object:
    """
    Asynchronously gets an item from a TraitQueue wrapping an SMQueue.
    """
    if not hasattr(queue, "_async_reader"):
        # Cache the async_reader instance on the queue wrapper.
        queue._async_reader = queue.queue.async_reader()
    return await queue._async_reader.next()
