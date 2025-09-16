import time
from multiprocessing import get_context

import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    RetryableTrait,
    retryable,
    task,
)
from wombat.multiprocessing.systems import RetryableSystem
from wombat.multiprocessing.traits.lifecycle import Failed, Succeeded
from wombat.multiprocessing.traits.models import Prop
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---
@task
def always_fail_task(_worker: Worker):
    """A task that always fails to test max_tries."""
    raise ValueError("This task is designed to fail.")


@task
def fail_n_times_task(worker: Worker, fail_count: int) -> str:
    """
    Fails `fail_count` times, then succeeds. Uses a shared counter to track attempts.
    """
    attempt_counter = worker.props["attempt_counter"].instance
    with attempt_counter.get_lock():
        attempt_counter.value += 1
        current_attempt = attempt_counter.value

    if current_attempt <= fail_count:
        raise ValueError(f"Failing on attempt {current_attempt}")
    return f"Succeeded on attempt {current_attempt}"


def custom_backoff_func(trait: "RetryableTrait") -> float:
    """A custom backoff function that just returns a fixed value."""
    return 0.1


# --- Fixture ---


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    """Fixture for a retry-enabled orchestrator."""
    context = get_context("spawn")
    # A shared counter for tasks to track their attempts.
    attempt_counter = context.Value("i", 0)

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([always_fail_task, fail_n_times_task])
        .with_systems([RetryableSystem])
        .add_prop(
            "attempt_counter",
            Prop(initializer=attempt_counter, use_context_manager=False),
        )
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        # Reset counter before each test
        with attempt_counter.get_lock():
            attempt_counter.value = 0
        yield orch


# --- Tests ---


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retryable_succeeds_after_one_failure(orchestrator: Orchestrator):
    """Tests a task that fails once, is retried, and then succeeds."""
    retry_task_def = retryable(max_tries=2, initial_delay=0.01)(fail_n_times_task)

    await orchestrator.add_task(retry_task_def(fail_count=1))
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    result = results[0]

    check.is_true(any(isinstance(t, Succeeded) for t in result.traits))
    check.equal(result.result, "Succeeded on attempt 2")

    # Check the final state of the Retryable trait
    retry_trait = next((t for t in result.traits if isinstance(t, RetryableTrait)), None)
    check.is_not_none(retry_trait)
    check.equal(retry_trait.tries, 1)


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retryable_fails_after_exhausting_tries(orchestrator: Orchestrator):
    """Tests that a task is marked as Failed after exhausting all retries."""
    retry_task_def = retryable(max_tries=2, initial_delay=0.01)(always_fail_task)

    await orchestrator.add_task(retry_task_def())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)
    result = results[0]

    check.is_true(any(isinstance(t, Failed) for t in result.traits))

    retry_trait = next((t for t in result.traits if isinstance(t, RetryableTrait)), None)
    check.is_not_none(retry_trait)
    check.equal(retry_trait.tries, 2)


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retryable_linear_backoff(orchestrator: Orchestrator):
    """Tests the timing of the linear backoff strategy."""
    initial_delay = 0.2
    retry_task_def = retryable(
        max_tries=2, initial_delay=initial_delay, backoff_strategy="linear"
    )(fail_n_times_task)

    start_time = time.monotonic()
    fail_count = 2
    await orchestrator.add_task(retry_task_def(fail_count=fail_count))
    await orchestrator.finish_tasks()
    end_time = time.monotonic()

    duration = end_time - start_time

    # Expected delays: 0.2s (try 1), 0.4s (try 2) -> total ~0.6s
    expected_duration = sum(initial_delay * i for i in range(1, fail_count + 1))
    check.is_true(duration >= expected_duration)
    check.is_true(duration < expected_duration + 0.3)  # Allow for overhead


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retryable_exponential_backoff(orchestrator: Orchestrator):
    """Tests the timing of the exponential backoff strategy."""
    initial_delay = 0.1
    multiplier = 2.0
    retry_task_def = retryable(
        max_tries=3,
        initial_delay=initial_delay,
        backoff_strategy="exponential",
        backoff_multiplier=multiplier,
    )(fail_n_times_task)

    start_time = time.monotonic()
    await orchestrator.add_task(retry_task_def(fail_count=3))
    await orchestrator.finish_tasks()
    end_time = time.monotonic()

    duration = end_time - start_time

    # Expected delays:
    # 1. 0.1 * (2**0) = 0.1s
    # 2. 0.1 * (2**1) = 0.2s
    # 3. 0.1 * (2**2) = 0.4s
    # Total delay = 0.1 + 0.2 + 0.4 = 0.7s
    expected_duration = (
        initial_delay * (multiplier**0)
        + initial_delay * (multiplier**1)
        + initial_delay * (multiplier**2)
    )
    check.is_true(duration >= expected_duration)
    check.is_true(duration < expected_duration + 0.3)  # Allow for overhead


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retryable_custom_backoff(orchestrator: Orchestrator):
    """Tests a custom backoff function."""
    retry_task_def = retryable(
        max_tries=1,
        backoff_strategy="custom",
        backoff_function=custom_backoff_func,
    )(fail_n_times_task)

    start_time = time.monotonic()
    await orchestrator.add_task(retry_task_def(fail_count=1))
    await orchestrator.finish_tasks()
    end_time = time.monotonic()

    duration = end_time - start_time

    # Custom function returns a fixed 0.1s
    expected_duration = 0.1
    check.is_true(duration >= expected_duration)
    check.is_true(duration < expected_duration + 0.3)
