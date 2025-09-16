from multiprocessing import get_context

import pytest
import pytest_check as check

from wombat.multiprocessing import (
    OrchestratorBuilder,
    produces,
    task,
)
from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict
from wombat.multiprocessing.systems import ProducesSystem
from wombat.multiprocessing.traits.models import Task
from wombat.multiprocessing.worker import Worker


# --- Test Actions ---


@task
def child_succeeds(_worker: Worker) -> str:
    return "success"


@task
def child_fails(_worker: Worker):
    raise ValueError("fail")


@produces()
@task
def producer(_worker: Worker, num_success: int, num_fail: int) -> list[Task]:
    """Produces a mix of succeeding and failing child tasks."""
    return [child_succeeds() for _ in range(num_success)] + [
        child_fails() for _ in range(num_fail)
    ]


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_orchestrator_progress_bar_e2e():
    """
    Tests the full end-to-end progress bar integration by running an orchestrator
    and checking the final metrics captured from the progress process.
    """
    context = get_context("spawn")
    capture_dict = None
    try:
        capture_dict = SharedMemoryDict.create(
            context=context, purpose="progress_test_capture"
        )
        num_success = 3
        num_fail = 2
        num_workers = 2

        builder = (
            OrchestratorBuilder()
            .with_workers(num_workers=num_workers)
            .with_actions([producer, child_succeeds, child_fails])
            .with_systems([ProducesSystem])
            .with_progress_bar(True)
            .with_metrics(capture_dict)
            .without_logging()
        )

        async with builder.build() as orchestrator:
            await orchestrator.add_task(
                producer(num_success=num_success, num_fail=num_fail)
            )
            await orchestrator.finish_tasks()

        # The progress process shuts down and populates capture_dict upon exiting
        # the 'async with' block.

        # --- Assert Final Metrics ---
        check.is_true("Total" in capture_dict, "Total metrics not found in capture_dict")
        total_metrics = capture_dict["Total"]

        # 1 initial producer task
        check.equal(total_metrics.get("initial"), 1)
        # 5 generated child tasks
        check.equal(total_metrics.get("generated"), num_success + num_fail)
        # Producer (1) + successful children (3)
        check.equal(total_metrics.get("completed"), 1 + num_success)
        # Failing children (2)
        check.equal(total_metrics.get("failures"), num_fail)
        # Check other counts are zero
        check.equal(total_metrics.get("retries", 0), 0)
        check.equal(total_metrics.get("skipped", 0), 0)
        check.equal(total_metrics.get("cancelled", 0), 0)
        check.equal(total_metrics.get("expired", 0), 0)

        # Verify worker counts add up to the total
        worker_initial = 0
        worker_generated = 0
        worker_completed = 0
        worker_failures = 0

        for i in range(num_workers):
            worker_key = f"worker-{i}"
            if worker_key in capture_dict:
                worker_metrics = capture_dict[worker_key]
                worker_initial += worker_metrics.get("initial", 0)
                worker_generated += worker_metrics.get("generated", 0)
                worker_completed += worker_metrics.get("completed", 0)
                worker_failures += worker_metrics.get("failures", 0)

        check.equal(worker_initial, total_metrics.get("initial"))
        check.equal(worker_generated, total_metrics.get("generated"))
        check.equal(worker_completed, total_metrics.get("completed"))
        check.equal(worker_failures, total_metrics.get("failures"))

    finally:
        if capture_dict is not None:
            capture_dict.close()
            capture_dict.unlink()
