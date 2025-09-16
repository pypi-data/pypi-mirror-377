import asyncio
from multiprocessing import get_context
from queue import Empty, Full
from typing import Any

import pytest
import pytest_check as check
from pydantic import BaseModel

from wombat.multiprocessing.errors import UnserializablePayloadError
from wombat.multiprocessing.ipc.queues.trait_queue import TraitQueue, implicitly_is
from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict

# --- Test SharedMemoryDict ---


def _smd_writer_process(smd_state: tuple, key: Any, value: Any):
    """Target function for a child process to write to a SharedMemoryDict."""
    smd = SharedMemoryDict.__new__(SharedMemoryDict)
    smd.__setstate__(smd_state)
    smd[key] = value
    smd.close()


def _smd_incrementer_process(smd_state: tuple, key: str, increments: int):
    """Target function for a child process to increment a value in a SharedMemoryDict."""
    smd = SharedMemoryDict.__new__(SharedMemoryDict)
    smd.__setstate__(smd_state)
    for _ in range(increments):
        with smd.lock:
            data = smd._read_data()
            current_value = data.get(key, 0)
            data[key] = current_value + 1
            smd._write_data(data)
    smd.close()


@pytest.mark.timeout(5)
def test_shared_memory_dict_basic_ops():
    """Tests basic dictionary operations on a SharedMemoryDict."""
    context = get_context("spawn")
    smd = None
    try:
        smd = SharedMemoryDict.create(context=context, purpose="test_basic_ops")
        smd["a"] = 1
        smd["b"] = {"c": 3}

        check.equal(len(smd), 2)
        check.is_in("a", smd)
        check.is_not_in("d", smd)
        check.equal(smd["a"], 1)
        check.equal(smd.get("b"), {"c": 3})

        del smd["a"]
        check.equal(len(smd), 1)
        check.is_not_in("a", smd)

    finally:
        if smd:
            try:
                smd.close()
            except Exception as e:
                print(f"[DEBUG-TEST] Exception during smd.close(): {e!r}")
            smd.unlink()


@pytest.mark.timeout(10)
def test_shared_memory_dict_cross_process():
    """Tests that SharedMemoryDict is accessible and modifiable across processes."""
    context = get_context("spawn")
    smd = None
    try:
        smd = SharedMemoryDict.create(context=context, purpose="test_cross_process")
        smd["parent_key"] = "parent_value"

        smd_state = smd.__getstate__()
        p = context.Process(
            target=_smd_writer_process, args=(smd_state, "child_key", "child_value")
        )
        p.start()
        p.join(timeout=5)
        check.equal(p.exitcode, 0)

        check.equal(len(smd), 2)
        check.equal(smd["parent_key"], "parent_value")
        check.equal(smd["child_key"], "child_value")

    finally:
        if smd:
            smd.close()
            smd.unlink()


@pytest.mark.timeout(5)
def test_shared_memory_dict_exceeds_size():
    """Tests that SharedMemoryDict raises ValueError when data exceeds max_size."""
    context = get_context("spawn")
    smd = None
    try:
        smd = SharedMemoryDict.create(
            context=context, max_size=32, purpose="test_exceeds_size"
        )
        with check.raises(ValueError):
            smd["big_data"] = "this string is definitely larger than 32 bytes"
    finally:
        if smd is not None:
            smd.close()
            smd.unlink()


@pytest.mark.timeout(15)
def test_shared_memory_dict_concurrent_access():
    """Tests that SharedMemoryDict handles concurrent writes correctly using its lock."""
    context = get_context("spawn")
    smd = None
    try:
        smd = SharedMemoryDict.create(context=context, purpose="test_concurrent")
        smd["counter"] = 0
        num_processes = 4
        increments_per_process = 100

        smd_state = smd.__getstate__()
        processes = []
        for _ in range(num_processes):
            p = context.Process(
                target=_smd_incrementer_process,
                args=(smd_state, "counter", increments_per_process),
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join(timeout=10)
            check.equal(p.exitcode, 0)

        expected_value = num_processes * increments_per_process
        check.equal(smd["counter"], expected_value)

    finally:
        if smd:
            smd.close()
            smd.unlink()


# --- Test TraitQueue (wrapping SMQueue) ---


class SimpleModel(BaseModel):
    x: int


class ValidModel(BaseModel):
    pass


class InvalidModel(BaseModel):
    pass


def _trait_queue_producer(queue_state: dict, items: list):
    """Target function for a child process to put items in a TraitQueue."""
    q = TraitQueue.__new__(TraitQueue)
    q.__setstate__(queue_state)
    for item in items:
        q.put_blocking(item)
    q.close()


@pytest.mark.timeout(5)
def test_trait_queue_basic_ops():
    """Tests basic put and get operations on a TraitQueue."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(context=context, name="test_q", slots=4, slot_size=1024)
        item1 = SimpleModel(x=1)
        item2 = SimpleModel(x=2)

        q.put_nowait(item1)
        q.put_nowait(item2)

        check.is_false(q.empty())

        retrieved1 = q.get_nowait()
        retrieved2 = q.get_nowait()

        check.equal(retrieved1, item1.model_dump(mode="python"))
        check.equal(retrieved2, item2.model_dump(mode="python"))

        check.is_true(q.empty())
        with pytest.raises(Empty):
            q.get_nowait()
    finally:
        if q:
            q.close()
            q.unlink()


@pytest.mark.timeout(5)
def test_trait_queue_full_behavior():
    """Tests that a full queue raises Full on put_nowait."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(context=context, name="test_q_full", slots=1, slot_size=1024)
        q.put_nowait(SimpleModel(x=1))
        check.is_true(q.full())
        with pytest.raises(Full):
            q.put_nowait(SimpleModel(x=2))
    finally:
        if q:
            q.close()
            q.unlink()


@pytest.mark.timeout(10)
def test_trait_queue_cross_process():
    """Tests sending and receiving items across processes using TraitQueue."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(context=context, name="test_q_mp", slots=5, slot_size=1024)
        items_to_send = [SimpleModel(x=i) for i in range(5)]

        queue_state = q.__getstate__()
        p = context.Process(
            target=_trait_queue_producer, args=(queue_state, items_to_send)
        )
        p.start()

        received_items = []
        for _ in range(len(items_to_send)):
            # get() is blocking
            received_items.append(q.get(timeout=2))

        p.join(timeout=5)
        check.equal(p.exitcode, 0)

        check.equal(len(received_items), len(items_to_send))
        for i, item_dict in enumerate(received_items):
            check.equal(item_dict["x"], items_to_send[i].x)

    finally:
        if q:
            q.close()
            q.unlink()


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_trait_queue_async_reader():
    """Tests the asyncio-compatible reader for TraitQueue."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(context=context, name="test_q_async", slots=3, slot_size=1024)

        async def producer():
            await asyncio.sleep(0.01)
            q.put(SimpleModel(x=1))
            await asyncio.sleep(0.01)
            q.put(SimpleModel(x=2))
            await asyncio.sleep(0.01)
            q.put(SimpleModel(x=3))

        producer_task = asyncio.create_task(producer())

        reader = q.queue.async_reader()

        item1 = await reader.next()
        item2 = await reader.next()
        item3 = await reader.next()

        await producer_task

        check.equal(item1, {"x": 1})
        check.equal(item2, {"x": 2})
        check.equal(item3, {"x": 3})

    finally:
        if q:
            q.close()
            q.unlink()


def _trait_queue_join_worker(queue_state: dict):
    """Worker that gets items and calls task_done."""
    q = TraitQueue.__new__(TraitQueue)
    q.__setstate__(queue_state)
    for _ in range(2):
        q.get(timeout=2)
        q.task_done()
    q.close()


@pytest.mark.timeout(10)
def test_trait_queue_joinable():
    """Tests the join() and task_done() functionality of a joinable queue."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(
            context=context, name="test_q_join", joinable=True, slots=2, slot_size=1024
        )

        q.put(SimpleModel(x=1))
        q.put(SimpleModel(x=2))

        queue_state = q.__getstate__()
        p = context.Process(target=_trait_queue_join_worker, args=(queue_state,))
        p.start()

        # This should block until the worker has called task_done for all items
        q.join()

        p.join(timeout=5)
        check.equal(p.exitcode, 0)

    finally:
        if q:
            q.close()
            q.unlink()


@pytest.mark.timeout(5)
def test_trait_queue_oversized_payload():
    """Tests that putting an oversized payload raises UnserializablePayloadError."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(context=context, name="test_q_oversized", slots=1, slot_size=10)
        big_item = {"data": "this string is much larger than 10 bytes"}
        with pytest.raises(UnserializablePayloadError):
            q.put(big_item)
    finally:
        if q:
            q.close()
            q.unlink()


@pytest.mark.timeout(5)
def test_trait_queue_validation():
    """Tests the validation logic of TraitQueue."""
    context = get_context("spawn")
    q = None
    try:
        q = TraitQueue(
            context=context,
            name="test_q_validation",
            validator=implicitly_is,
            validation_list=[ValidModel],
            slots=2,
            slot_size=1024,
        )

        # Test with put()
        check.is_true(q.put(ValidModel()))  # Should succeed
        check.is_false(q.put(InvalidModel()))  # Should fail validation and return False

        # Test with put_nowait()
        q.get_nowait()  # Clear the queue
        q.put_nowait(ValidModel())  # Should succeed
        q.put_nowait(InvalidModel())  # Should be a no-op due to validation failure

        # Verify only the valid model was added
        q.get_nowait()
        with pytest.raises(Empty):
            q.get_nowait()

        # Test with put_blocking()
        q.put_blocking(ValidModel())
        with pytest.raises(ValueError, match="Item failed validation for queue."):
            q.put_blocking(InvalidModel())

    finally:
        if q:
            q.close()
            q.unlink()
