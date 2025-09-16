import asyncio
import os
import signal

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    pinned,
    task,
)
from wombat.multiprocessing.systems import PinnedSystem
from wombat.multiprocessing.errors import WorkerCrashError
from wombat.multiprocessing.traits.lifecycle import Succeeded
from wombat.multiprocessing.worker import Worker


# Test Actions
@task
def simple_sync_task(_worker: Worker, x: int, y: int) -> int:
    return x + y


@task
async def simple_async_task(_worker: Worker, x: int, y: int) -> int:
    await asyncio.sleep(0.01)
    return x * y


@task
def worker_name_task(worker: Worker) -> str:
    return worker.identity.name


@task
def crash_worker_task(_worker: Worker):
    os.kill(os.getpid(), signal.SIGKILL)


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    """Fixture to provide a started orchestrator and ensure it's shut down."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions(
            [simple_sync_task, simple_async_task, worker_name_task, crash_worker_task]
        )
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_e2e_lifecycle(orchestrator: Orchestrator):
    """Tests the basic end-to-end lifecycle of submitting tasks and getting results."""
    tasks = [simple_sync_task(1, 2), simple_async_task(3, 4)]
    await orchestrator.add_tasks(tasks)
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 2)

    sync_result = next(r for r in results if r.action == simple_sync_task.action_name)
    async_result = next(r for r in results if r.action == simple_async_task.action_name)

    check.is_true(any(isinstance(t, Succeeded) for t in sync_result.traits))
    check.equal(sync_result.result, 3)
    check.is_true(any(isinstance(t, Succeeded) for t in async_result.traits))
    check.equal(async_result.result, 12)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_task_distribution_with_pinning():
    """Tests that the Pinned trait correctly routes tasks to a specific worker."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([worker_name_task])
        .with_systems([PinnedSystem])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        pinned_task_def_0 = pinned(worker_name="worker-0")(worker_name_task)
        pinned_task_def_1 = pinned(worker_name="worker-1")(worker_name_task)
        pinned_task_0 = pinned_task_def_0()
        pinned_task_1 = pinned_task_def_1()

        await orchestrator.add_tasks([pinned_task_0, pinned_task_1])
        await orchestrator.finish_tasks()

        results = {r.id: r for r in orchestrator.get_results()}
        check.equal(len(results), 2)
        check.equal(results[pinned_task_0.id].result, "worker-0")
        check.equal(results[pinned_task_1.id].result, "worker-1")


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_get_results_clears_buffer(orchestrator: Orchestrator):
    """Tests that get_results is a one-time operation that clears the internal buffer."""
    await orchestrator.add_task(simple_sync_task(5, 5))
    await orchestrator.finish_tasks()

    results1 = list(orchestrator.get_results())
    check.equal(len(results1), 1)
    check.equal(results1[0].result, 10)

    results2 = list(orchestrator.get_results())
    check.equal(len(results2), 0)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_handles_worker_crash():
    """Tests that the orchestrator raises WorkerCrashError when a worker dies."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([crash_worker_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(crash_worker_task())

        with pytest.raises(WorkerCrashError):
            await orchestrator.finish_tasks()


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_shutdown_with_context_manager():
    """Tests that the async context manager correctly shuts down the orchestrator."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(simple_sync_task(1, 1))
        # No call to finish_tasks, __aexit__ should handle shutdown

    # The test passes if no errors are raised and it doesn't hang.
    check.is_true(orchestrator.stopped)


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_add_task_and_add_tasks(orchestrator: Orchestrator):
    """Tests both single and batch task submission methods."""
    # Single task
    task1 = simple_sync_task(1, 1)
    await orchestrator.add_task(task1)

    # Batch of tasks
    tasks2 = [simple_sync_task(2, 2), simple_sync_task(3, 3)]
    await orchestrator.add_tasks(tasks2)

    await orchestrator.finish_tasks()

    results = sorted([r.result for r in orchestrator.get_results()])
    check.equal(results, [2, 4, 6])


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_orchestrator_with_zero_workers():
    """Tests that the orchestrator can run and shut down with zero workers."""
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=0)
        .with_actions([simple_sync_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(simple_sync_task(1, 1))
        # With no workers, this should return immediately.
        await orchestrator.finish_tasks()
        results = list(orchestrator.get_results())
        # No tasks should have executed.
        check.equal(len(results), 0)

    # The test passes if it completes without hanging.


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_add_tasks_with_unserializable_arg():
    """
    Tests that add_tasks handles unserializable arguments gracefully by returning
    them in the `enqueue_failures` list.
    """
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_sync_task])
        .without_logging()
    )
    async with builder.build() as orchestrator:
        # Lambda functions are not serializable by the custom encoder.
        task_with_bad_arg = simple_sync_task(x=1, y=lambda: 2)

        failures = await orchestrator.add_tasks([task_with_bad_arg])

        check.equal(len(failures), 1)
        check.equal(failures[0].id, task_with_bad_arg.id)

        # Verify no tasks were actually run.
        await orchestrator.finish_tasks()
        results = list(orchestrator.get_results())
        check.equal(len(results), 0)
