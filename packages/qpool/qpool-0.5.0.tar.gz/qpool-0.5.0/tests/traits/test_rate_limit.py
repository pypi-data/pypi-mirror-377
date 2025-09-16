import time
from datetime import timedelta

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    rate_limit,
    task,
)
from wombat.multiprocessing.systems import RateLimitSystem
from wombat.multiprocessing.worker import Worker


# --- Test Action ---

@rate_limit(limit=2, period=timedelta(seconds=0.5), group="test_limit")
@task
def limited_action(_worker: Worker) -> float:
    return time.monotonic()


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2) # Use multiple workers to test concurrency safety
        .with_actions([limited_action])
        .with_systems([RateLimitSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_rate_limit_throttles_tasks(orchestrator: Orchestrator):
    """Tests that the rate limit spreads out task execution over time."""
    start_time = time.monotonic()
    
    tasks_to_run = [limited_action() for _ in range(4)]
    await orchestrator.add_tasks(tasks_to_run)
    await orchestrator.finish_tasks()
    
    end_time = time.monotonic()
    
    duration = end_time - start_time
    
    # With a limit of 2 per 0.5s, 4 tasks should take at least 0.5s.
    # The first two run immediately. The next two run after the first period expires.
    check.is_true(duration >= 0.5)
    # And not excessively long
    check.is_true(duration < 1.0)
