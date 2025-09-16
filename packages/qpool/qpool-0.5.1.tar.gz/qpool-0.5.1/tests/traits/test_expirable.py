from datetime import timedelta

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    delayed,
    expirable,
    task,
)
from wombat.multiprocessing.systems import DelayedSystem, ExpirableSystem
from wombat.multiprocessing.traits.lifecycle import Expired, Succeeded
from wombat.multiprocessing.worker import Worker

# --- Test Actions ---

@task
def simple_action(_worker: Worker) -> str:
    return "executed"


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([simple_action])
        .with_systems([ExpirableSystem, DelayedSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_expirable_task_is_skipped(orchestrator: Orchestrator):
    """Tests that an expired task is skipped and marked with the Expired trait."""
    # This task expires in 0.1s but is delayed for 0.3s, so it should expire.
    expirable_action = delayed(delay=0.3)(expirable(expires_after=timedelta(seconds=0.1))(simple_action))

    await orchestrator.add_task(expirable_action())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    check.is_true(any(isinstance(t, Expired) for t in results[0].traits))


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_expirable_task_succeeds(orchestrator: Orchestrator):
    """Tests that a non-expired task executes successfully."""
    # This task expires in 0.3s and is delayed for 0.1s, so it should run.
    expirable_action = delayed(delay=0.1)(expirable(expires_after=timedelta(seconds=0.3))(simple_action))

    await orchestrator.add_task(expirable_action())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    check.is_true(any(isinstance(t, Succeeded) for t in results[0].traits))
