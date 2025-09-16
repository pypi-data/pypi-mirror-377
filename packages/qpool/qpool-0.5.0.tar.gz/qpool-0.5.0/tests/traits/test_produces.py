import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    produces,
    task,
)
from wombat.multiprocessing.systems import ProducesSystem
from wombat.multiprocessing.traits.lifecycle import Succeeded
from wombat.multiprocessing.traits.models import Task
from wombat.multiprocessing.worker import Worker

# --- Test Actions ---


@task
def final_task(_worker: Worker, value: int) -> int:
    """A simple terminal task that returns a value."""
    return value


@produces()
@task
def producer_task_single(_worker: Worker) -> Task:
    """Produces a single new task."""
    return final_task(value=10)


@produces()
@task
def producer_task_list(_worker: Worker) -> list[Task]:
    """Produces a list of new tasks."""
    return [final_task(value=20), final_task(value=30)]


# --- Fixture ---


@pytest_asyncio.fixture
async def orchestrator() -> Orchestrator:
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([final_task, producer_task_single, producer_task_list])
        .with_systems([ProducesSystem])
        .without_logging()
    )
    orch = builder.build()
    async with orch:
        yield orch


# --- Tests ---


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_produces_single_task(orchestrator: Orchestrator):
    """
    Tests that a producer returning a single task correctly queues and
    executes the new task, and its own result is suppressed.
    """
    await orchestrator.add_task(producer_task_single())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # We should only get the result from the `final_task`.
    check.equal(len(results), 1)

    result = results[0]
    check.is_true(any(isinstance(t, Succeeded) for t in result.traits))
    check.equal(result.action, final_task.action_name)
    check.equal(result.result, 10)


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_produces_list_of_tasks(orchestrator: Orchestrator):
    """
    Tests that a producer returning a list of tasks correctly queues and
    executes all new tasks, and its own result is suppressed.
    """
    await orchestrator.add_task(producer_task_list())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())

    # We should get two results, one for each `final_task`.
    check.equal(len(results), 2)

    results.sort(key=lambda r: r.result)

    check.is_true(all(r.action == final_task.action_name for r in results))
    check.is_true(all(any(isinstance(t, Succeeded) for t in r.traits) for r in results))
    check.equal([r.result for r in results], [20, 30])
