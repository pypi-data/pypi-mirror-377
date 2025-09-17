import asyncio
import logging
from functools import partial

from wombat.multiprocessing import (
    OrchestratorBuilder,
    task,
)
from wombat.multiprocessing.systems import LoggableSystem
from wombat.multiprocessing.worker import Worker


# 1. Define a generic task action with an option to enable logging.
def process_data(worker: Worker, data: str, log: bool = False) -> str:
    """A simple task that processes some data."""
    processed_data = data.upper()
    if log:
        worker.log(f"Processed '{data}' into '{processed_data}'", logging.INFO)
    else:
        # For demonstration, we can add a debug log for the quiet version.
        worker.log(f"Quietly processed '{data}'", logging.DEBUG)
    return processed_data


# 2. Create multiple TaskDefinitions from the same action using functools.partial.
#    This allows creating specialized versions of a task action.

# A "verbose" version of the task that logs at INFO level.
verbose_process_data = task(partial(process_data, log=True))

# A "quiet" version of the task that will only log at DEBUG level.
quiet_process_data = task(process_data)


# 3. Use the Orchestrator to run instances of both task definitions.
async def main():
    # Configure logging to see the messages in the console.
    logging_config = {"to_console": True, "level": logging.INFO}

    async with (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([verbose_process_data, quiet_process_data])
        .with_logging(logging_config)
        .with_systems([LoggableSystem])
        .build()
    ) as orchestrator:
        # Create task instances from each definition.
        task1 = verbose_process_data(data="hello")
        task2 = quiet_process_data(data="world")
        task3 = verbose_process_data(data="again")

        # Add the tasks to the pool.
        await orchestrator.add_tasks([task1, task2, task3])

        # Wait for the tasks to complete.
        await orchestrator.finish_tasks()
        results = list(orchestrator.get_results())

        print("\n--- Results ---")
        for r in sorted(results, key=lambda res: res.result):
            print(f"Task {r.id} ({r.action}) finished with result: '{r.result}'")
        print(
            "Note: You should see INFO logs for 'hello' and 'again', but not for 'world' "
            "(as its log is at DEBUG level)."
        )


if __name__ == "__main__":
    asyncio.run(main())
