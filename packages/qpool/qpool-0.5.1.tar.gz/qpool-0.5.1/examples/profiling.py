import asyncio
import logging

from wombat.multiprocessing import OrchestratorBuilder, task
from wombat.multiprocessing.worker import Worker


@task
async def cpu_bound_action(_worker: Worker, n: int = 100_000):
    """A simple CPU-bound task that does some calculations."""
    total = 0
    for i in range(n):
        total += i * i
    return total


async def main():
    """
    This example demonstrates how to enable line-profiling for workers.

    When profiling is enabled, each worker will generate .prof files in the
    profiles/ directory, and can optionally print stats to the console.
    """
    # Basic logging config to see worker startup messages.
    logging_config = {"to_console": True, "level": logging.INFO}

    # Build the orchestrator, enabling profiling.
    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([cpu_bound_action])
        .with_logging(logging_config)
        .with_profiling(enabled=True, to_console=True)
    )

    async with builder.build() as orchestrator:
        tasks = [cpu_bound_action() for _ in range(10)]
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()
        list(orchestrator.get_results())


if __name__ == "__main__":
    asyncio.run(main())
