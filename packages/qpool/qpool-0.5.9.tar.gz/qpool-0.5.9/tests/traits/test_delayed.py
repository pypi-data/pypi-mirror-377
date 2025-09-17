import time

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    delayed,
    task,
)
from wombat.multiprocessing.systems import DelayedSystem
from wombat.multiprocessing.worker import Worker

# --- Test Action ---

@delayed(delay=0.2)
@task
def delayed_action(_worker: Worker) -> str:
    return "done"


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([delayed_action])
        .with_systems([DelayedSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_delayed_task(orchestrator: Orchestrator):
    """Tests that the Delayed trait waits before executing the task."""
    start_time = time.monotonic()
    
    await orchestrator.add_task(delayed_action())
    await orchestrator.finish_tasks()
    
    end_time = time.monotonic()
    
    duration = end_time - start_time
    
    # Check that the total duration is at least the delay time
    check.is_true(duration >= 0.2)
    # And not excessively long
    check.is_true(duration < 0.5)
