from __future__ import annotations

from multiprocessing.context import BaseContext
from queue import Empty, Full
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type, TypeVar

from pydantic import BaseModel

from wombat.multiprocessing.errors import UnserializablePayloadError
from wombat.multiprocessing.ipc.queues.smqueue import SMQueue, SMQueueSpec

if TYPE_CHECKING:
    from wombat.multiprocessing.traits.models import BaseTrait

T = TypeVar("T", bound=BaseModel)


def explicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any(item.__class__ == model for model in models)


def implicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any(isinstance(item, model) for model in models)


def task_validator(item: BaseModel, required_traits: List[Type["BaseTrait"]]) -> bool:
    """
    Validates that an item is a Task, and if `required_traits` is provided,
    ensures the task possesses at least one of those traits.
    """
    # Local import to avoid circular dependency
    from wombat.multiprocessing.traits.models import Task

    if not isinstance(item, Task):
        return False

    if not required_traits:
        return True

    task_trait_types = {type(trait) for trait in getattr(item, "traits", [])}
    required_trait_set = set(required_traits)
    return not task_trait_types.isdisjoint(required_trait_set)


class TraitQueue:
    """
    A high-level wrapper around an `SMQueue` that handles Pydantic model
    serialization and optional validation.

    This class provides a familiar `queue.Queue`-like interface but operates
    on top of a shared memory ring buffer for high-performance, cross-process
    communication. It automatically converts Pydantic models to dictionaries
    before enqueuing.
    """

    name: str
    joinable: bool = False
    queue: SMQueue
    validator: Callable[..., bool]
    validation_list: List[Any]
    context: BaseContext

    def __init__(
        self,
        context: BaseContext,
        name: str,
        joinable: bool = False,
        validator: Optional[Callable[..., bool]] = None,
        validation_list: Optional[List[Any]] = None,
        slots: int = 4096,
        slot_size: int = 128000,
    ):
        self.context = context
        self.name = name
        self.joinable = joinable
        self.validator = validator
        self.validation_list = validation_list or []
        self.queue, self.spec, self.ipc = SMQueue.create(
            context=context, slots=slots, slot_size=slot_size, joinable=joinable
        )
        self.closed = False

    def __getstate__(self):
        """Prepare the TraitQueue for pickling by saving its spec and IPC handles."""
        return {
            "name": self.name,
            "joinable": self.joinable,
            "validator": self.validator,
            "validation_list": self.validation_list,
            "spec": self.spec,
            "ipc": self.ipc,
            "closed": self.closed,
        }

    def __setstate__(self, state):
        """Reconstruct the TraitQueue in a new process by attaching to shared memory."""
        self.__dict__.update(state)
        if isinstance(self.spec, dict):
            self.spec = SMQueueSpec(**self.spec)
        self.queue = SMQueue.attach(self.spec, self.ipc)
        if "closed" not in self.__dict__:
            self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.join()

    def put(self, item: T) -> bool:
        if self.validator and not self.validator(item, self.validation_list):
            return False
        try:
            # For performance, Pydantic models are serialized to dicts before being
            # passed to the underlying msgpack-based queue.
            if isinstance(item, BaseModel):
                payload = item.model_dump(mode="python")
            else:
                payload = item

            self.queue.put_nowait(payload)
            return True
        except ValueError as e:
            # ValueError for oversized items, others for msgpack/pickle errors
            raise UnserializablePayloadError(
                f"Failed to serialize object of type {type(item).__name__} for queue '{self.name}'. Reason: {e!s}"
            ) from e
        except Full:
            return False

    def put_blocking(self, item: T) -> None:
        """
        Puts an item onto the queue, blocking until a slot is available.
        This method is intended to be called from within a thread pool executor.
        """
        if self.validator and not self.validator(item, self.validation_list):
            # We can't easily return False here as the caller in the executor
            # won't check it. Raising an error is better.
            raise ValueError("Item failed validation for queue.")
        try:
            if isinstance(item, BaseModel):
                payload = item.model_dump(mode="python")
            else:
                payload = item
            # This calls the blocking put on the underlying SMQueue.
            self.queue.put(payload)
        except ValueError as e:
            raise UnserializablePayloadError(
                f"Failed to serialize object of type {type(item).__name__} for queue '{self.name}'. Reason: {e!s}"
            ) from e

    def get(self, block: bool = True, timeout: Optional[float] = None) -> BaseModel:
        if not block:
            return self.get_nowait()
        return self.queue.get(timeout=timeout)

    def task_done(self):
        if not self.joinable:
            return
        self.queue.task_done()

    def join(self) -> None:
        if self.joinable:
            self.queue.join()

    def empty(self):
        # This is an approximation with SMQueue, as it doesn't expose size directly.
        return self.queue.full_sem.get_value() == 0

    def full(self):
        # This is an approximation with SMQueue.
        return self.queue.empty_sem.get_value() == 0

    def get_nowait(self) -> BaseModel:
        try:
            return self.queue.get_nowait()
        except RuntimeError as e:
            if "empty" in str(e):
                raise Empty from e
            raise

    def put_nowait(self, obj):
        if self.validator and not self.validator(obj, self.validation_list):
            return

        if isinstance(obj, BaseModel):
            payload = obj.model_dump(mode="python")
        else:
            payload = obj
        self.queue.put_nowait(payload)

    def close(self):
        self.closed = True
        if hasattr(self, "_async_reader"):
            reader = self._async_reader
            if reader._installed:
                try:
                    reader._loop.remove_reader(reader._fd)
                except Exception:
                    # Ignore errors during shutdown, e.g., if loop is already closing.
                    pass
                reader._installed = False
        return self.queue.close()

    def unlink(self):
        return self.queue.unlink()
