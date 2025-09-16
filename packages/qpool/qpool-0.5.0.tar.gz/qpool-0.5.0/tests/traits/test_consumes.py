import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    consumes,
    produces,
    task,
)
from wombat.multiprocessing.systems import ConsumesSystem, ProducesSystem
from wombat.multiprocessing.traits.lifecycle import Succeeded
from wombat.multiprocessing.traits.models import Task
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---


@task
def child_task(_worker: Worker, value: int) -> int:
    """A simple child task that returns a value."""
    return value * 2


@produces(tags=["batch1"])
@task
def producer_task(_worker: Worker, num_children: int) -> list[Task]:
    """Produces a batch of child tasks."""
    return [child_task(value=i) for i in range(num_children)]


@consumes(tags=["batch1"], batch_size=5)
@task
def consumer_task(_worker: Worker, consumed_results: list[int] | None = None) -> int:
    """Consumes the results of the child tasks and sums them."""
    if consumed_results is None:
        return -1  # Should not happen
    return sum(consumed_results)


# --- Fixture ---


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([producer_task, child_task, consumer_task])
        .with_systems([ProducesSystem, ConsumesSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


# --- Test ---


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_produces_consumes_workflow(orchestrator: Orchestrator):
    """
    Tests the full fan-out/fan-in workflow:
    1. A producer creates a batch of child tasks with a tag.
    2. A consumer is submitted to wait for results with the same tag.
    3. The orchestrator runs the child tasks.
    4. Once the batch is complete, the orchestrator emits the consumer.
    5. The consumer receives the collected results and produces a final result.
    """
    # Add the consumer first. It will be held by the orchestrator until its
    # dependencies are met. Then, add the producer which will generate the work.
    await orchestrator.add_tasks([consumer_task(), producer_task(num_children=5)])

    # This waits for all initial tasks *and* all dynamically generated tasks
    # (including the emitted consumer) to complete.
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # We should only get the final result from the `consumer_task`. The producer's
    # result is suppressed, and the children's results are consumed.
    check.equal(len(results), 1)

    result = results[0]
    check.is_true(any(isinstance(t, Succeeded) for t in result.traits))
    check.equal(result.action, consumer_task.action_name)

    # Expected results from children: [0*2, 1*2, 2*2, 3*2, 4*2] -> [0, 2, 4, 6, 8]
    # The consumer sums them: 0 + 2 + 4 + 6 + 8 = 20
    check.equal(result.result, 20)
