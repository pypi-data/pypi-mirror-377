import asyncio
from datetime import timedelta

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    debounce,
    task,
)
from wombat.multiprocessing.systems import DebounceSystem
from wombat.multiprocessing.traits.lifecycle import Skipped, Succeeded
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---

@debounce(window=timedelta(seconds=0.2))
@task
def debounced_action(_worker: Worker, x: int) -> int:
    return x

@debounce(window=timedelta(seconds=0.2), group="group1")
@task
def grouped_action_a(_worker: Worker, x: int) -> int:
    return x

@debounce(window=timedelta(seconds=0.2), group="group1")
@task
def grouped_action_b(_worker: Worker, x: int) -> int:
    return x


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([debounced_action, grouped_action_a, grouped_action_b])
        .with_systems([DebounceSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_debounce_skips_duplicate_task(orchestrator: Orchestrator):
    """Tests that a duplicate task within the window is skipped."""
    task1 = debounced_action(x=1)
    task2 = debounced_action(x=1)
    
    await orchestrator.add_tasks([task1, task2])
    await orchestrator.finish_tasks()
    
    results = {r.id: r for r in orchestrator.get_results()}
    check.equal(len(results), 2)
    
    check.is_true(any(isinstance(t, Succeeded) for t in results[task1.id].traits))
    check.is_true(any(isinstance(t, Skipped) for t in results[task2.id].traits))


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_debounce_allows_task_after_window(orchestrator: Orchestrator):
    """Tests that a duplicate task after the window is executed."""
    await orchestrator.add_task(debounced_action(x=1))
    await orchestrator.finish_tasks()
    list(orchestrator.get_results())  # Clear the results buffer

    await asyncio.sleep(0.3)
    
    await orchestrator.add_task(debounced_action(x=1))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    # First result is cleared by first finish_tasks, this gets the second one
    check.equal(len(results), 1)
    check.is_true(any(isinstance(t, Succeeded) for t in results[0].traits))


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_debounce_differentiates_by_args(orchestrator: Orchestrator):
    """Tests that tasks with different arguments are not debounced against each other."""
    await orchestrator.add_tasks([debounced_action(x=1), debounced_action(x=2)])
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 2)
    check.is_true(all(any(isinstance(t, Succeeded) for t in r.traits) for r in results))

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_debounce_groups_tasks(orchestrator: Orchestrator):
    """Tests that tasks in the same group are debounced against each other."""
    task1 = grouped_action_a(x=10)
    task2 = grouped_action_b(x=20) # Same group, different action
    
    await orchestrator.add_tasks([task1, task2])
    await orchestrator.finish_tasks()
    
    results = {r.id: r for r in orchestrator.get_results()}
    check.equal(len(results), 2)
    
    check.is_true(any(isinstance(t, Succeeded) for t in results[task1.id].traits))
    check.is_true(any(isinstance(t, Skipped) for t in results[task2.id].traits))
