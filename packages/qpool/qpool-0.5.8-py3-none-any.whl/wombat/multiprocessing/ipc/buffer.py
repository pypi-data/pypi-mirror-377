from __future__ import annotations

import enum
import struct
from dataclasses import dataclass
from multiprocessing import shared_memory
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from multiprocessing.context import BaseContext
    from multiprocessing.synchronize import Semaphore as SemaphoreClass

_HEADER = struct.Struct(">I")  # 4-byte big-endian payload length for data length


class BufferState(enum.Enum):
    EMPTY = 0
    READY_FOR_WORKER = 1
    WORKER_PROCESSING = 2


class BufferConfig(BaseModel):
    """Configuration for a shared memory buffer."""

    size: int = 256 * 2048  # Default to 0.5MB


@dataclass(frozen=True)
class BufferHandle:
    """Specification to attach to a shared memory buffer."""

    shm_name: str
    size: int


class Buffer:
    """
    A single-slot, shared memory buffer for efficiently sending batches of tasks.

    This class encapsulates a shared memory block and the necessary synchronization
    primitives (locks, events, semaphores) to coordinate between a single
    producer (the orchestrator) and a single consumer (a worker).
    """

    def __init__(
        self,
        context: BaseContext,
        size: int,
        create: bool = False,
    ):
        if create:
            self.shm = shared_memory.SharedMemory(create=True, size=size)
        else:
            # This path is not used in the current design, but is here for completeness.
            # Workers will receive the buffer directly, not re-attach.
            raise NotImplementedError(
                "Attaching to BatchBuffer by spec is not implemented."
            )

        self.spec = BufferHandle(shm_name=self.shm.name, size=size)
        self.buf = self.shm.buf
        self.lock = context.Lock()
        self.state = context.Value("i", BufferState.EMPTY.value)
        self.data_length = context.Value("i", 0)
        self.wakeup_rx, self.wakeup_tx = context.Pipe(duplex=False)
        # This new pipe signals to the orchestrator that a worker is ready for a new batch.
        self.producer_ready_rx, self.producer_ready_tx = context.Pipe(duplex=False)
        self.producer_semaphore: SemaphoreClass = context.Semaphore(1)

    def __getstate__(self) -> dict[str, Any]:
        """
        Serializes the buffer's specification and IPC handles for pickling.

        This allows the buffer object to be transferred to a worker process,
        which can then re-attach to the underlying shared memory and sync
        primitives.
        """
        return {
            "spec": self.spec,
            "lock": self.lock,
            "state": self.state,
            "data_length": self.data_length,
            "wakeup_rx": self.wakeup_rx,
            "wakeup_tx": self.wakeup_tx,
            "producer_ready_rx": self.producer_ready_rx,
            "producer_ready_tx": self.producer_ready_tx,
            "producer_semaphore": self.producer_semaphore,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Reconstructs the Buffer in a new process by attaching to shared memory."""
        self.spec = state["spec"]
        self.lock = state["lock"]
        self.state = state["state"]
        self.data_length = state["data_length"]
        self.wakeup_rx = state["wakeup_rx"]
        self.wakeup_tx = state["wakeup_tx"]
        self.producer_ready_rx = state["producer_ready_rx"]
        self.producer_ready_tx = state["producer_ready_tx"]
        self.producer_semaphore = state["producer_semaphore"]
        self.shm = shared_memory.SharedMemory(name=self.spec.shm_name)
        self.buf = self.shm.buf

    def close_and_unlink(self) -> None:
        """
        Closes and unlinks the shared memory. To be called by the creator process.

        This ensures that the shared memory segment is properly cleaned up from
        the system upon orchestrator shutdown.
        """
        self.buf = None
        self.shm.close()
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass  # May have already been unlinked.

    def close(self) -> None:
        """Closes the shared memory view. To be called by consumer processes."""
        self.buf = None
        self.shm.close()
