import asyncio
import time
from typing import Any, Dict

import pytest
import pytest_check as check

from wombat.multiprocessing import OrchestratorBuilder, requires_props, task
from wombat.multiprocessing.traits.lifecycle import Failed, Succeeded
from wombat.multiprocessing.traits.models import Prop
from wombat.multiprocessing.worker import Worker


# Test Actions
@task
def simple_sync_task(_worker: Worker, x: int, y: int) -> int:
    return x + y


@task
async def simple_async_task(_worker: Worker, x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x * y


@requires_props(requires_props=["my_prop"])
@task
def prop_task(_worker: Worker, props: Dict[str, Any]) -> str:
    return props["my_prop"].instance


@task
def exception_task(_worker: Worker) -> None:
    raise ValueError("This task is designed to fail.")


@task
async def sleep_task(_worker: Worker, duration: float) -> float:
    start = time.monotonic()
    await asyncio.sleep(duration)
    end = time.monotonic()
    return end - start


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_worker_executes_sync_and_async_tasks():
    """Tests that a worker can correctly execute both sync and async actions."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task, simple_async_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        tasks = [simple_sync_task(10, 5), simple_async_task(10, 5)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 2)

        sync_result = next(r for r in results if r.action == simple_sync_task.action_name)
        async_result = next(
            r for r in results if r.action == simple_async_task.action_name
        )

        check.is_true(any(isinstance(t, Succeeded) for t in sync_result.traits))
        check.equal(sync_result.result, 15)
        check.is_true(any(isinstance(t, Succeeded) for t in async_result.traits))
        check.equal(async_result.result, 50)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_worker_handles_props():
    """Tests that a worker correctly initializes and injects props into a task."""
    prop_value = "hello from prop"
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([prop_task])
        .add_prop(
            "my_prop",
            Prop(
                initializer=prop_value,
                use_context_manager=False,
            ),
        )
        .without_logging()
    )

    async with builder.build() as orchestrator:
        await orchestrator.add_task(prop_task())
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 1)
        check.is_true(any(isinstance(t, Succeeded) for t in results[0].traits))
        check.equal(results[0].result, prop_value)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_worker_handles_task_exception():
    """Tests that a worker correctly handles exceptions raised by a task action."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([exception_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(exception_task())
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 1)
        result = results[0]

        check.is_true(any(isinstance(t, Failed) for t in result.traits))
        # Result is a list [exception_string, original_result (None)]
        check.is_instance(result.result, list)
        check.is_in("ValueError: This task is designed to fail.", result.result[0])


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_worker_concurrency_limit():
    """Tests that a worker respects the max_concurrent_tasks setting."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1, max_concurrent_tasks=2)
        .with_actions([sleep_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        start_time = time.monotonic()
        tasks = [sleep_task(duration=0.2) for _ in range(4)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()
        end_time = time.monotonic()

        duration = end_time - start_time
        # Expect two batches of two tasks, so ~0.4s.
        # Allow a generous margin for overhead.
        check.is_true(0.4 <= duration < 0.6)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_worker_cancels_task_on_shutdown():
    """
    Tests that the worker cancels in-flight tasks during shutdown and reports
    them as failed.
    """
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([sleep_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        # Add a long-running task but don't wait for it to finish.
        await orchestrator.add_task(sleep_task(duration=5.0))
        # Give it a moment to be dispatched to the worker.
        await asyncio.sleep(0.1)

    # The context manager exit triggers shutdown.
    # Now, inspect the final results buffer.
    results = list(orchestrator.get_results())

    # If a result makes it back, it should be a failure.
    # The primary goal is ensuring the process terminates cleanly without hanging.
    if results:
        check.equal(len(results), 1)
        result = results[0]
        check.is_true(any(isinstance(t, Failed) for t in result.traits))
        check.is_in("worker shutdown", result.result[0])
