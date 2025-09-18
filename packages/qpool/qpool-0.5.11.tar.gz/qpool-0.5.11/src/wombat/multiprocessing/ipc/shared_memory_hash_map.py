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
    from multiprocessing.synchronize import RLock as LockClass

# Slot header: 8-byte hash (unsigned long long), 4-byte data length (unsigned int)
_SLOT_HEADER = struct.Struct(">QI")
_EMPTY_SLOT = b"\x00" * _SLOT_HEADER.size
# A tombstone marks a deleted slot, allowing probes to continue past it.
# The hash is max u64, a value that `hash()` is unlikely to produce.
_TOMBSTONE = struct.pack(">QI", 2**64 - 1, 0)


class SharedMemoryHashMap(MutableMapping):
    """
    A dictionary-like object using a hash map in a shared memory block.

    This class provides a thread-safe and process-safe way to share key-value
    data. It uses a fixed number of slots and linear probing for collision
    resolution, avoiding the need to serialize/deserialize the entire map on
    each access.
    """

    def __init__(self, name: str, lock: LockClass, capacity: int, slot_size: int):
        self._shm = shared_memory.SharedMemory(name=name)
        self._lock = lock
        self.capacity = capacity
        self.slot_size = slot_size
        self._total_slot_size = _SLOT_HEADER.size + self.slot_size
        self.name = name
        # The first 8 bytes of the SHM block store the item count.
        self._count_view = self._shm.buf[:8]

    @property
    def lock(self) -> LockClass:
        """Returns the lock used by this SharedMemoryHashMap instance."""
        return self._lock

    @classmethod
    def create(
        cls,
        context: BaseContext,
        capacity: int = 4096,
        slot_size: int = 2048,
        purpose: str = "unknown",
    ) -> "SharedMemoryHashMap":
        """Creates a new shared memory block for the hash map."""
        total_shm_size = 8 + (
            capacity * (_SLOT_HEADER.size + slot_size)
        )  # 8 bytes for count
        name = f"wombat_shm_hashmap_{purpose}_{os.getpid()}_{os.urandom(4).hex()}"
        shm = shared_memory.SharedMemory(name=name, create=True, size=total_shm_size)
        lock = context.RLock()

        # Initialize count to zero.
        shm.buf[:8] = struct.pack(">Q", 0)
        shm.close()

        return cls(name=name, lock=lock, capacity=capacity, slot_size=slot_size)

    def _get_hash(self, key: Any) -> int:
        # Use Python's built-in hash, but ensure it's a positive 64-bit integer.
        return hash(key) & (2**64 - 1)

    def _find_slot(self, key: Any) -> tuple[int, int | None]:
        """
        Finds the slot for a key using linear probing with tombstones.

        Returns a tuple of (insert_index, found_index).
        - If the key is found, `found_index` is its index, and `insert_index` is the same.
        - If not found, `found_index` is None, and `insert_index` is the first
          empty or tombstone slot available for insertion.
        """
        target_hash = self._get_hash(key)
        start_index = target_hash % self.capacity
        first_tombstone = None

        for i in range(self.capacity):
            index = (start_index + i) % self.capacity
            offset = 8 + (index * self._total_slot_size)
            header_bytes = self._shm.buf[offset : offset + _SLOT_HEADER.size]

            if header_bytes == _EMPTY_SLOT:
                # End of probe chain. Use the first tombstone if we saw one.
                return (
                    first_tombstone if first_tombstone is not None else index
                ), None

            if header_bytes == _TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = index
                continue  # Continue probing for an existing key.

            slot_hash, data_len = _SLOT_HEADER.unpack(header_bytes)
            if slot_hash == target_hash:
                # Hash match, now check the actual key
                data_offset = offset + _SLOT_HEADER.size
                packed_data = self._shm.buf[data_offset : data_offset + data_len]
                stored_key, _ = msgpack.unpackb(packed_data, raw=False)
                if stored_key == key:
                    return index, index  # Key found

        if first_tombstone is not None:
            return first_tombstone, None

        raise MemoryError("Hash map is full.")

    def __setitem__(self, key: Any, value: Any):
        with self._lock:
            insert_index, existing_index = self._find_slot(key)
            is_new_item = existing_index is None

            packed_data = msgpack.packb(
                (key, value), default=default_encoder, use_bin_type=True
            )
            if len(packed_data) > self.slot_size:
                raise ValueError(
                    f"Packed data size ({len(packed_data)}) exceeds slot size ({self.slot_size})"
                )

            target_hash = self._get_hash(key)
            header = _SLOT_HEADER.pack(target_hash, len(packed_data))
            offset = 8 + (insert_index * self._total_slot_size)
            self._shm.buf[offset : offset + _SLOT_HEADER.size] = header
            data_offset = offset + _SLOT_HEADER.size
            self._shm.buf[data_offset : data_offset + len(packed_data)] = packed_data

            if is_new_item:
                current_count = struct.unpack(">Q", self._count_view)[0]
                self._count_view[:8] = struct.pack(">Q", current_count + 1)

    def __getitem__(self, key: Any) -> Any:
        with self._lock:
            _, index = self._find_slot(key)
            if index is None:
                raise KeyError(key)

            offset = 8 + (index * self._total_slot_size)
            _, data_len = _SLOT_HEADER.unpack(
                self._shm.buf[offset : offset + _SLOT_HEADER.size]
            )
            data_offset = offset + _SLOT_HEADER.size
            packed_data = self._shm.buf[data_offset : data_offset + data_len]
            _, value = msgpack.unpackb(packed_data, raw=False)
            return value

    def __delitem__(self, key: Any):
        with self._lock:
            _, index = self._find_slot(key)
            if index is None:
                raise KeyError(key)

            offset = 8 + (index * self._total_slot_size)
            self._shm.buf[offset : offset + _SLOT_HEADER.size] = _TOMBSTONE

            current_count = struct.unpack(">Q", self._count_view)[0]
            self._count_view[:8] = struct.pack(">Q", current_count - 1)

    def items(self) -> list[tuple[Any, Any]]:
        """Returns a list of all (key, value) pairs in the hash map."""
        with self._lock:
            item_list = []
            count = len(self)
            if count == 0:
                return item_list

            checked_slots = 0
            found_items = 0
            while checked_slots < self.capacity and found_items < count:
                offset = 8 + (checked_slots * self._total_slot_size)
                header_bytes = self._shm.buf[offset : offset + _SLOT_HEADER.size]
                if header_bytes != _EMPTY_SLOT and header_bytes != _TOMBSTONE:
                    _, data_len = _SLOT_HEADER.unpack(header_bytes)
                    data_offset = offset + _SLOT_HEADER.size
                    packed_data = self._shm.buf[data_offset : data_offset + data_len]
                    key, value = msgpack.unpackb(packed_data, raw=False)
                    item_list.append((key, value))
                    found_items += 1
                checked_slots += 1
            return item_list

    def clear(self):
        """Removes all items from the hash map."""
        with self._lock:
            self._count_view[:8] = struct.pack(">Q", 0)
            for i in range(self.capacity):
                offset = 8 + (i * self._total_slot_size)
                self._shm.buf[offset : offset + _SLOT_HEADER.size] = _EMPTY_SLOT

    def __len__(self) -> int:
        with self._lock:
            return struct.unpack(">Q", self._count_view)[0]

    def __iter__(self) -> Iterator[Any]:
        """Creates an iterator for the keys in the hash map."""
        # This approach is safe for modification during iteration because it iterates
        # over a snapshot of the keys.
        with self._lock:
            key_list = []
            count = len(self)
            if count > 0:
                checked_slots = 0
                found_items = 0
                while checked_slots < self.capacity and found_items < count:
                    offset = 8 + (checked_slots * self._total_slot_size)
                    header_bytes = self._shm.buf[offset : offset + _SLOT_HEADER.size]
                    if header_bytes != _EMPTY_SLOT and header_bytes != _TOMBSTONE:
                        _, data_len = _SLOT_HEADER.unpack(header_bytes)
                        data_offset = offset + _SLOT_HEADER.size
                        packed_data = self._shm.buf[
                            data_offset : data_offset + data_len
                        ]
                        key, _ = msgpack.unpackb(packed_data, raw=False)
                        key_list.append(key)
                        found_items += 1
                    checked_slots += 1
            return iter(key_list)

    def _read_data(self) -> dict:
        """Reads the entire map into a new dictionary."""
        return dict(self.items())

    def _write_data(self, data: dict):
        """Writes an entire dict, overwriting existing data."""
        self.clear()
        for key, value in data.items():
            self[key] = value

    def close(self):
        # The memoryview must be released before the underlying shm can be closed.
        if hasattr(self, "_count_view"):
            self._count_view.release()
        self._shm.close()

    def unlink(self):
        try:
            shm = shared_memory.SharedMemory(name=self.name)
            shm.unlink()
            shm.close()
        except FileNotFoundError:
            pass

    def __getstate__(self):
        return self.name, self._lock, self.capacity, self.slot_size

    def __setstate__(self, state):
        name, lock, capacity, slot_size = state
        self.name = name
        self._lock = lock
        self.capacity = capacity
        self.slot_size = slot_size
        self._total_slot_size = _SLOT_HEADER.size + self.slot_size
        self._shm = shared_memory.SharedMemory(name=name)
        self._count_view = self._shm.buf[:8]
