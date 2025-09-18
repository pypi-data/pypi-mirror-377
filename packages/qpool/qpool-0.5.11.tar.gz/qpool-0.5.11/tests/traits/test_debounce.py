import asyncio
from datetime import timedelta

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    debounce,
    task,
)
from wombat.multiprocessing.systems import DebounceSystem
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
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([debounced_action, grouped_action_a, grouped_action_b])
        .with_systems([DebounceSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
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

    results_list = list(results.values())
    succeeded_tasks = [
        r
        for r in results_list
        if any(
            isinstance(t, StateTrait) and t.outcome == TaskOutcome.SUCCESS
            for t in r.traits
        )
    ]
    skipped_tasks = [
        r
        for r in results_list
        if any(
            isinstance(t, StateTrait) and t.outcome == TaskOutcome.SKIPPED
            for t in r.traits
        )
    ]
    check.equal(len(succeeded_tasks), 1)
    check.equal(len(skipped_tasks), 1)


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
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
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait)
    check.equal(state_trait.outcome, TaskOutcome.SUCCESS)


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_debounce_differentiates_by_args(orchestrator: Orchestrator):
    """Tests that tasks with different arguments are not debounced against each other."""
    await orchestrator.add_tasks([debounced_action(x=1), debounced_action(x=2)])
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 2)
    for r in results:
        state_trait = next((t for t in r.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(state_trait)
        check.equal(state_trait.outcome, TaskOutcome.SUCCESS)

@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
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

    results_list = list(results.values())
    succeeded_tasks = [
        r
        for r in results_list
        if any(
            isinstance(t, StateTrait) and t.outcome == TaskOutcome.SUCCESS
            for t in r.traits
        )
    ]
    skipped_tasks = [
        r
        for r in results_list
        if any(
            isinstance(t, StateTrait) and t.outcome == TaskOutcome.SKIPPED
            for t in r.traits
        )
    ]
    check.equal(len(succeeded_tasks), 1)
    check.equal(len(skipped_tasks), 1)
