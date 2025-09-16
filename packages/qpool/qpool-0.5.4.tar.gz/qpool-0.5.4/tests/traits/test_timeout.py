import asyncio

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    task,
    timeout,
)
from wombat.multiprocessing.systems import TimeoutSystem
from wombat.multiprocessing.traits.lifecycle import Cancelled, Succeeded
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---

@task
async def sleep_task(_worker: Worker, duration: float):
    await asyncio.sleep(duration)
    return "done"


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([sleep_task])
        .with_systems([TimeoutSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_timeout_cancels_long_task(orchestrator: Orchestrator):
    """Tests that a task is cancelled if it exceeds its timeout."""
    timed_out_task = timeout(timeout=0.1)(sleep_task)
    
    await orchestrator.add_task(timed_out_task(duration=0.5))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    check.is_true(any(isinstance(t, Cancelled) for t in results[0].traits))


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_timeout_allows_short_task(orchestrator: Orchestrator):
    """Tests that a task succeeds if it finishes before its timeout."""
    successful_task = timeout(timeout=0.5)(sleep_task)
    
    await orchestrator.add_task(successful_task(duration=0.1))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    check.is_true(any(isinstance(t, Succeeded) for t in results[0].traits))
