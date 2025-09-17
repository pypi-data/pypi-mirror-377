# SMQueue.py
"""
Shared-memory multi-producer / single-consumer ring queue for Python.

- Fixed number of slots, each with a fixed maximum payload size.
- Cross-process safe using multiprocessing semaphores/locks/values.
- Stores arbitrary Python objects via msgpack (protocol=highest).
- Blocking get(), non-blocking get_nowait(), and an asyncio reader.

Typical pattern (parent creates; children attach using spec/ipc):

    from multiprocessing import Process

    q_parent, spec, ipc = SMQueue.create(slots=4096, slot_size=4096)

    def worker(spec, ipc):
        q = SMQueue.attach(spec, ipc)
        for i in range(1000):
            q.put(("hello", i))

    p = Process(target=worker, args=(spec, ipc), daemon=True); p.start()

    # consumer (in parent)
    for _ in range(1000):
        item = q_parent.get()
        ...

    p.join()
    q_parent.close(); q_parent.unlink()   # unlink only once (creator)

Notes
-----
* This implementation assumes **one logical consumer** draining the queue.
  (Multiple producers are supported.)
* If you want asyncio consumption, use q.async_reader() to receive items
  without blocking the event loop.
"""

from __future__ import annotations

import asyncio
import os
import struct
from dataclasses import dataclass
from multiprocessing import (
    Condition,
    Lock,
    Semaphore,
    Value,
    connection,
    shared_memory,
)
from multiprocessing.context import BaseContext
from queue import Empty, Full
from typing import Any, Dict, Optional, Tuple

import msgpack

from wombat.multiprocessing.ipc.utilities import default_encoder

# ---------------- Internals ----------------

_HEADER = struct.Struct(">I")  # 4-byte big-endian payload length


@dataclass(frozen=True)
class SMQueueSpec:
    """Specification required to attach to the shared memory region."""

    name: str
    slots: int
    slot_size: int


class AsyncReader:
    """
    Internal helper that integrates the queue with asyncio by:
    - Using a pipe to get wakeups when producers put() items.
    - Draining as many items as are immediately available without blocking.
    """

    __slots__ = ("_loop", "_q", "_fd", "_out", "_installed", "_draining")

    def __init__(self, q: "SMQueue"):
        self._loop = asyncio.get_running_loop()
        self._q = q
        self._fd = q.notify_rx.fileno()
        self._out: asyncio.Queue[Any] = asyncio.Queue()
        self._installed = False
        self._draining = False
        self._ensure_reader()
        self._drain_items()

    def _ensure_reader(self) -> None:
        if self._installed:
            return
        self._loop.add_reader(self._fd, self._on_readable)
        self._installed = True

    def _on_readable(self) -> None:
        try:
            while self._q.notify_rx.poll():
                try:
                    self._q.notify_rx.recv_bytes()
                except (EOFError, OSError):
                    break
        except Exception:
            pass
        self._drain_items()

    def _drain_items(self) -> None:
        if self._draining:
            return
        self._draining = True
        try:
            while True:
                try:
                    item = self._q.get_nowait()
                    self._out.put_nowait(item)
                except RuntimeError as e:
                    if str(e) == "empty":
                        break
                    raise
        finally:
            self._draining = False

    async def next(self) -> Any:
        self._drain_items()
        try:
            return self._out.get_nowait()
        except asyncio.QueueEmpty:
            pass
        return await self._out.get()

    # Async iterator convenience
    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.next()
        except asyncio.CancelledError:
            raise
        except Exception:
            raise StopAsyncIteration


class SMQueue:
    """
    A shared-memory ring buffer queue.

    Use SMQueue.create(...) in the creator process, then pass (spec, ipc)
    to child processes and call SMQueue.attach(spec, ipc) there.
    """

    # --------- Construction / lifecycle ---------

    def __init__(
        self,
        spec: SMQueueSpec,
        *,
        full_sem: Semaphore,
        empty_sem: Semaphore,
        head_lock: Lock,
        tail_lock: Lock,
        head_idx: Value,  # 'Q' (unsigned long long)
        tail_idx: Value,  # 'Q'
        notify_tx: connection.Connection,
        notify_rx: connection.Connection,
        unfinished_tasks: Optional[Value] = None,
        finished_cond: Optional[Condition] = None,
        create: bool = False,
    ) -> None:
        self.spec = spec
        self._slot_span = 4 + spec.slot_size  # 4 bytes length + payload
        if create:
            # Initialize shared memory with zero-length headers.
            self._shm = shared_memory.SharedMemory(
                create=True,
                size=self._slot_span * spec.slots,
                name=spec.name,
            )
            buf = self._shm.buf
            for i in range(spec.slots):
                off = i * self._slot_span
                buf[off : off + 4] = _HEADER.pack(0)
        else:
            self._shm = shared_memory.SharedMemory(name=spec.name, create=False)

        self.buf = self._shm.buf

        # Cross-process sync primitives (created by parent; passed to children)
        self.full_sem = full_sem
        self.empty_sem = empty_sem
        self.head_lock = head_lock
        self.tail_lock = tail_lock
        self.head_idx = head_idx
        self.tail_idx = tail_idx

        # One-byte wakeups for asyncio reader
        self.notify_tx = notify_tx
        self.notify_rx = notify_rx
        self.unfinished_tasks = unfinished_tasks
        self.finished_cond = finished_cond

    # Public factory for the creator/owner
    @classmethod
    def create(
        cls, *, context: BaseContext, slots: int, slot_size: int, joinable: bool = False
    ) -> Tuple["SMQueue", SMQueueSpec, Dict[str, Any]]:
        """
        Create a new shared-memory queue and return (queue, spec, ipc).

        - spec: pass to other processes so they can attach to the same
                shared memory region by name.
        - ipc:  a picklable dict of synchronization primitives and pipes
                that must also be passed to children.
        """
        if slots <= 0:
            raise ValueError("slots must be > 0")
        if slot_size <= 0:
            raise ValueError("slot_size must be > 0")

        name = f"smq_{os.getpid()}_{os.urandom(4).hex()}"
        spec = SMQueueSpec(name=name, slots=slots, slot_size=slot_size)

        full_sem = context.Semaphore(0)
        empty_sem = context.Semaphore(slots)
        head_lock = context.Lock()
        tail_lock = context.Lock()
        head_idx = context.Value("Q", 0)
        tail_idx = context.Value("Q", 0)

        # Notify pipe for asyncio wakeups.
        rx, tx = context.Pipe(duplex=False)

        q_args = dict(
            full_sem=full_sem,
            empty_sem=empty_sem,
            head_lock=head_lock,
            tail_lock=tail_lock,
            head_idx=head_idx,
            tail_idx=tail_idx,
            notify_tx=tx,
            notify_rx=rx,
        )

        ipc = q_args.copy()

        if joinable:
            unfinished_tasks = context.Value("i", 0)
            finished_cond = context.Condition(context.Lock())
            ipc["unfinished_tasks"] = unfinished_tasks
            ipc["finished_cond"] = finished_cond
            q_args["unfinished_tasks"] = unfinished_tasks
            q_args["finished_cond"] = finished_cond

        q = cls(
            spec,
            **q_args,
            create=True,
        )
        return q, spec, ipc

    # Public factory for children (attach to existing queue)
    @classmethod
    def attach(cls, spec: SMQueueSpec, ipc: Dict[str, Any]) -> "SMQueue":
        return cls(
            spec,
            full_sem=ipc["full_sem"],
            empty_sem=ipc["empty_sem"],
            head_lock=ipc["head_lock"],
            tail_lock=ipc["tail_lock"],
            head_idx=ipc["head_idx"],
            tail_idx=ipc["tail_idx"],
            notify_tx=ipc["notify_tx"],
            notify_rx=ipc["notify_rx"],
            unfinished_tasks=ipc.get("unfinished_tasks"),
            finished_cond=ipc.get("finished_cond"),
            create=False,
        )

    # Export the IPC handles (useful if you only have the queue object)
    def export_ipc(self) -> Dict[str, Any]:
        ipc = dict(
            full_sem=self.full_sem,
            empty_sem=self.empty_sem,
            head_lock=self.head_lock,
            tail_lock=self.tail_lock,
            head_idx=self.head_idx,
            tail_idx=self.tail_idx,
            notify_tx=self.notify_tx,
            notify_rx=self.notify_rx,
        )
        if self.unfinished_tasks:
            ipc["unfinished_tasks"] = self.unfinished_tasks
        if self.finished_cond:
            ipc["finished_cond"] = self.finished_cond
        return ipc

    # --------- Put / Get ---------

    def put(self, item: Any) -> None:
        """
        Enqueue an item (msgpacked) into the ring buffer.
        Blocks when the ring is full until a slot becomes available.
        """
        data = msgpack.packb(item, default=default_encoder, use_bin_type=True)

        # Wait for a free slot, then write to tail
        self.empty_sem.acquire()
        try:
            if self.finished_cond:
                with self.finished_cond:
                    self.unfinished_tasks.value += 1

            with self.tail_lock:
                idx = self.tail_idx.value
                self._write_slot(idx, data)
                self.tail_idx.value = idx + 1
        except Exception:
            # Restore state on failure
            self.empty_sem.release()
            if self.finished_cond:
                with self.finished_cond:
                    self.unfinished_tasks.value -= 1
            raise

        # Signal there is an additional full slot
        self.full_sem.release()

        # Try to send a single-byte wakeup
        try:
            self.notify_tx.send_bytes(b"\0")
        except (BrokenPipeError, OSError):
            # Pipe may be closed during shutdown
            pass
        except Exception:
            # Non-fatal; best-effort wakeup
            pass

    def put_nowait(self, item: Any) -> None:
        """
        Non-blocking enqueue. Raises queue.Full if no slot is free.
        """
        data = msgpack.packb(item, default=default_encoder, use_bin_type=True)

        if not self.empty_sem.acquire(block=False):
            raise Full

        try:
            if self.finished_cond:
                with self.finished_cond:
                    self.unfinished_tasks.value += 1

            with self.tail_lock:
                idx = self.tail_idx.value
                self._write_slot(idx, data)
                self.tail_idx.value = idx + 1
        except Exception:
            # Restore state on failure
            self.empty_sem.release()
            if self.finished_cond:
                with self.finished_cond:
                    self.unfinished_tasks.value -= 1
            raise

        # Signal there is an additional full slot
        self.full_sem.release()

        # Try to send a single-byte wakeup
        try:
            self.notify_tx.send_bytes(b"\0")
        except (BrokenPipeError, OSError):
            # Pipe may be closed during shutdown
            pass
        except Exception:
            # Non-fatal; best-effort wakeup
            pass

    def get(self, timeout: Optional[float] = None) -> Any:
        """
        Blocking dequeue.
        """
        if not self.full_sem.acquire(timeout=timeout):
            raise Empty

        try:
            with self.head_lock:
                idx = self.head_idx.value
                item = self._read_slot_deser(idx)
                self.head_idx.value = idx + 1
        finally:
            self.empty_sem.release()

        return item

    def get_nowait(self) -> Any:
        """Non-blocking dequeue. Raises RuntimeError('empty') if no item."""
        if not self.full_sem.acquire(block=False):
            raise RuntimeError("empty")
        try:
            with self.head_lock:
                idx = self.head_idx.value
                item = self._read_slot_deser(idx)
                self.head_idx.value = idx + 1
        finally:
            self.empty_sem.release()
        return item

    def task_done(self) -> None:
        """
        Indicate that a formerly enqueued task is complete.
        Used by joinable queues.
        """
        if self.finished_cond is None:
            raise ValueError("Not a joinable queue")
        with self.finished_cond:
            if self.unfinished_tasks.value == 0:
                raise ValueError("task_done() called too many times")
            self.unfinished_tasks.value -= 1
            if self.unfinished_tasks.value == 0:
                self.finished_cond.notify_all()

    def join(self) -> None:
        """
        Block until all items in the queue have been gotten and processed.
        """
        if self.finished_cond is None:
            raise ValueError("Not a joinable queue")
        with self.finished_cond:
            if self.unfinished_tasks.value > 0:
                self.finished_cond.wait()

    # --------- Async consumption ---------
    def async_reader(self) -> AsyncReader:
        """Return an asyncio-friendly reader object."""
        return AsyncReader(self)

    # --------- Low-level slot I/O ---------

    def _write_slot(self, idx: int, payload: bytes) -> None:
        if len(payload) > self.spec.slot_size:
            raise ValueError(
                f"Serialized object size {len(payload)} exceeds slot_size {self.spec.slot_size}"
            )
        off = (idx % self.spec.slots) * self._slot_span
        self.buf[off : off + 4] = _HEADER.pack(len(payload))
        self.buf[off + 4 : off + 4 + len(payload)] = payload

    def _read_slot_deser(self, idx: int) -> Any:
        off = (idx % self.spec.slots) * self._slot_span
        (length,) = _HEADER.unpack(self.buf[off : off + 4])
        payload = bytes(self.buf[off + 4 : off + 4 + length])
        return msgpack.unpackb(payload, raw=False)

    # --------- Cleanup ---------

    def close(self) -> None:
        """Detach from the shared memory segment."""
        try:
            self.notify_tx.close()
        except Exception:
            pass
        try:
            self.notify_rx.close()
        except Exception:
            pass
        try:
            self._shm.close()
        except Exception:
            pass

    def unlink(self) -> None:
        """
        Permanently remove the shared memory segment.
        Call this **only once**, from the creator process, after all users
        have closed the segment.
        """
        try:
            self._shm.unlink()
        except FileNotFoundError:
            pass
