from __future__ import annotations

import os
import struct
from collections.abc import MutableMapping
from multiprocessing import shared_memory
from typing import TYPE_CHECKING, Any, Iterator

import msgpack

from wombat.multiprocessing.ipc.utilities import default_encoder

if TYPE_CHECKING:
    from multiprocessing.context import BaseContext
    from multiprocessing.synchronize import Lock as LockClass


_HEADER_STRUCT = struct.Struct(">I")


class SharedMemoryDict(MutableMapping):
    """
    A dictionary-like object that stores its data in a shared memory block.

    This class provides a thread-safe and process-safe way to share a dictionary
    between multiple processes. Data is serialized using `msgpack`. It is intended
    for relatively small amounts of data that change frequently, such as state
    tracking for circuit breakers or rate limiters.

    The entire dictionary is read and written on each operation, so it is not
    performant for large datasets.
    """

    def __init__(self, name: str, lock: LockClass, size: int):
        self._shm = shared_memory.SharedMemory(name=name)
        self._lock = lock
        self._size = size
        self.name = name

    @property
    def lock(self) -> LockClass:
        """Returns the lock used by this SharedMemoryDict instance."""
        return self._lock

    @classmethod
    def create(
        cls,
        context: BaseContext,
        max_size: int = 16 * 1024,
        purpose: str = "unknown",
    ) -> "SharedMemoryDict":
        """
        Creates a new shared memory block and initializes it with an empty dictionary.

        Args:
            context: The multiprocessing context to use for creating locks.
            max_size: The maximum size of the shared memory block in bytes.
            purpose: A string to identify the purpose of the dictionary, included in its name.

        Returns:
            An instance of SharedMemoryDict attached to the new block.
        """
        name = f"wombat_shmemdict_{purpose}_{os.getpid()}_{os.urandom(4).hex()}"
        shm = shared_memory.SharedMemory(name=name, create=True, size=max_size)
        lock = context.Lock()

        empty_dict_packed = msgpack.packb({}, default=default_encoder, use_bin_type=True)
        shm.buf[:4] = _HEADER_STRUCT.pack(len(empty_dict_packed))
        shm.buf[4 : 4 + len(empty_dict_packed)] = empty_dict_packed
        shm.close()

        return cls(name=name, lock=lock, size=max_size)

    def _read_data(self) -> dict:
        """Reads the entire dictionary from shared memory."""
        data_len = _HEADER_STRUCT.unpack(self._shm.buf[:4])[0]
        if data_len == 0:
            return {}
        packed_data = bytes(self._shm.buf[4 : 4 + data_len])
        return msgpack.unpackb(packed_data, raw=False)

    def _write_data(self, data: dict) -> None:
        """Writes the entire dictionary to shared memory."""
        packed_data = msgpack.packb(data, default=default_encoder, use_bin_type=True)
        if len(packed_data) > self._size - 4:
            raise ValueError(
                f"Serialized dictionary size {len(packed_data)} exceeds shared memory buffer size {self._size - 4}"
            )
        self._shm.buf[:4] = _HEADER_STRUCT.pack(len(packed_data))
        self._shm.buf[4 : 4 + len(packed_data)] = packed_data

    def __contains__(self, key: Any) -> bool:
        with self._lock:
            return key in self._read_data()

    def __getitem__(self, key: Any) -> Any:
        with self._lock:
            data = self._read_data()
            return data[key]

    def __setitem__(self, key: Any, value: Any):
        with self._lock:
            data = self._read_data()
            data[key] = value
            self._write_data(data)

    def __delitem__(self, key: Any):
        with self._lock:
            data = self._read_data()
            del data[key]
            self._write_data(data)

    def __iter__(self) -> Iterator[Any]:
        with self._lock:
            return iter(self._read_data())

    def __len__(self) -> int:
        with self._lock:
            return len(self._read_data())

    def get(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            data = self._read_data()
            return data.get(key, default)

    def close(self) -> None:
        """Closes the view on the shared memory block."""
        self._shm.close()

    def unlink(self) -> None:
        """
        Unlinks the shared memory block from the system.

        This should only be called by the process that created the block,
        after all other processes have closed their views.
        """
        try:
            shm = shared_memory.SharedMemory(name=self.name)
            shm.unlink()
            shm.close()
        except FileNotFoundError:
            pass

    def __getstate__(self):
        return self.name, self._lock, self._size

    def __setstate__(self, state):
        name, lock, size = state
        self.name = name
        self._lock = lock
        self._size = size
        self._shm = shared_memory.SharedMemory(name=name)
