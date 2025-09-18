import pytest
import pytest_asyncio
import pytest_check as check

from wombat.multiprocessing import (
    Orchestrator,
    OrchestratorBuilder,
    tagged,
    task,
)
from wombat.multiprocessing.traits.tagged import TaggedTrait
from wombat.multiprocessing.worker import Worker


# --- Test Action ---
@tagged(tags=["tag1", "tag2"])
@task
def tagged_task(_worker: Worker) -> str:
    return "done"


@pytest_asyncio.fixture
async def orchestrator(request) -> Orchestrator:
    progress_bar_enabled = request.param
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([tagged_task])
        .without_logging()
        .with_progress_bar(progress_bar_enabled)
    )
    orch = builder.build()
    async with orch:
        yield orch


@pytest.mark.parametrize("orchestrator", [True, False], indirect=True)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_tagged_decorator_applies_trait(orchestrator: Orchestrator):
    """Tests that the @tagged decorator correctly applies a TaggedTrait to a task."""
    await orchestrator.add_task(tagged_task())
    await orchestrator.finish_tasks()

    results = list(orchestrator.get_results())
    check.equal(len(results), 1)

    result = results[0]
    tagged_trait = next((t for t in result.traits if isinstance(t, TaggedTrait)), None)

    check.is_not_none(tagged_trait)
    check.is_instance(tagged_trait, TaggedTrait)
    check.equal(tagged_trait.tags, ["tag1", "tag2"])
