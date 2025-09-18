import asyncio

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    StateTrait,
    TaskOutcome,
    breaker,
    task,
)
from wombat.multiprocessing.systems import BreakerSystem
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---


@breaker(failure_threshold=2, recovery_timeout=0.2, group="test_service")
@task
def service_task(_worker: Worker, should_fail: bool) -> str:
    if not should_fail:
        return "Success"
    raise ValueError("Service is down")


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([service_task])
        .with_systems([BreakerSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_breaker_opens_on_failures_and_skips_calls(orchestrator: Orchestrator):
    """Tests that the circuit opens after enough failures and skips new tasks."""
    # These two tasks should fail and trip the breaker (threshold=2)
    await orchestrator.add_task(service_task(should_fail=True))
    await orchestrator.add_task(service_task(should_fail=True))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 2)
    for r in results:
        state_trait = next((t for t in r.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(state_trait)
        check.equal(state_trait.outcome, TaskOutcome.FAILURE)

    # This task should be skipped immediately because the circuit is open
    await orchestrator.add_task(service_task(should_fail=True))
    await orchestrator.finish_tasks()
    
    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    # The task should be marked as failed by the breaker before execution
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait)
    check.equal(state_trait.outcome, TaskOutcome.FAILURE)


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_breaker_closes_after_recovery(orchestrator: Orchestrator):
    """Tests that the circuit transitions to half-open and then closes on success."""
    # Trip the breaker
    await orchestrator.add_tasks(
        [service_task(should_fail=True), service_task(should_fail=True)]
    )
    await orchestrator.finish_tasks()
    list(orchestrator.get_results()) # Clear buffer

    # Wait for the recovery timeout
    await asyncio.sleep(0.3)

    # The service is now healthy. The next call should be allowed (half-open)
    # and should succeed, closing the circuit.
    await orchestrator.add_task(service_task(should_fail=False))
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait)
    check.equal(state_trait.outcome, TaskOutcome.SUCCESS)

    # The circuit should now be closed. A subsequent call should also succeed.
    await orchestrator.add_task(service_task(should_fail=False))
    await orchestrator.finish_tasks()
    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    state_trait = next((t for t in results[0].traits if isinstance(t, StateTrait)), None)
    check.is_not_none(state_trait)
    check.equal(state_trait.outcome, TaskOutcome.SUCCESS)
