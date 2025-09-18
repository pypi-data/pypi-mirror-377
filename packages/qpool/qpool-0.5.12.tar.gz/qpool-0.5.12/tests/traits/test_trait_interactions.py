import asyncio

import pytest
import pytest_check as check

from wombat.multiprocessing import (
    OrchestratorBuilder,
    RetryableTrait,
    StateTrait,
    TaskOutcome,
    breaker,
    retryable,
    task,
    timeout,
)
from wombat.multiprocessing.systems import BreakerSystem, RetryableSystem, TimeoutSystem
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---
@task
async def slow_failing_task(_worker: Worker, fail: bool):
    """A task that is slow and can fail."""
    await asyncio.sleep(0.5)
    if fail:
        raise ValueError("Intentional failure")
    return "success"


# --- Tests for Retryable + Timeout ---


@pytest.mark.asyncio
@pytest.mark.timeout(5)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_retryable_with_timeout(progress_bar_enabled: bool):
    """
    Tests that a task with Retryable and Timeout is cancelled if an attempt
    exceeds the timeout, and that it does not retry.
    """
    # This task will time out on its first attempt and should be cancelled, not retried.
    test_task = timeout(timeout=0.1)(
        retryable(max_tries=2, initial_delay=0.01)(slow_failing_task)
    )

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([test_task])
        .with_systems([RetryableSystem, TimeoutSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        await orchestrator.add_task(test_task(fail=True))
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 1)

        result = results[0]
        state_trait = next((t for t in result.traits if isinstance(t, StateTrait)), None)
        check.is_not_none(state_trait)
        check.equal(state_trait.outcome, TaskOutcome.CANCELLED)
        # Verify it did not attempt to retry.
        retry_trait = next((t for t in result.traits if isinstance(t, RetryableTrait)), None)
        check.is_not_none(retry_trait)
        check.equal(retry_trait.tries, 0)


# --- Tests for Breaker + Retryable ---


@pytest.mark.asyncio
@pytest.mark.timeout(5)
@pytest.mark.parametrize("progress_bar_enabled", [True, False])
async def test_breaker_with_retryable(progress_bar_enabled: bool):
    """
    Tests that if a retryable task trips a circuit breaker, subsequent attempts
    (that would have been retries) are immediately failed by the open breaker.
    """
    # A task that will fail twice, tripping the breaker. It has retries available.
    test_task = breaker(failure_threshold=2, recovery_timeout=10.0)(
        retryable(max_tries=5, initial_delay=0.01)(slow_failing_task)
    )

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([test_task])
        .with_systems([BreakerSystem, RetryableSystem])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    async with builder.build() as orchestrator:
        # These two tasks will fail and open the circuit. They will also schedule retries.
        await orchestrator.add_task(test_task(fail=True))
        await orchestrator.add_task(test_task(fail=True))
        await orchestrator.finish_tasks()

        # At this point, two tasks have failed, and the breaker is open.
        # Two retry tasks have been scheduled and sent to the requeue.
        # The orchestrator will pick them up and try to run them.
        # The breaker's `before_task_execution` hook should run first and
        # immediately fail the tasks, preventing the retry logic from executing.
        # We need to wait for these retries to be processed.
        await orchestrator.finish_tasks()

        results = list(orchestrator.get_results())
        check.equal(len(results), 2)  # The 2 initial failures are suppressed; we only get the final failed retries.

        # All final results should be failures.
        for r in results:
            state_trait = next((t for t in r.traits if isinstance(t, StateTrait)), None)
            check.is_not_none(state_trait)
            check.equal(state_trait.outcome, TaskOutcome.FAILURE)

        # Verify that these failures are indeed from retry attempts that were
        # then failed by the open circuit breaker.
        for r in results:
            retry_trait = next(
                (t for t in r.traits if isinstance(t, RetryableTrait)), None
            )
            check.is_not_none(
                retry_trait, f"RetryableTrait not found on result for task {r.id}"
            )
            # The first failure schedules a retry, incrementing tries to 1.
            # That retry is then immediately failed by the open breaker.
            check.equal(retry_trait.tries, 1)
