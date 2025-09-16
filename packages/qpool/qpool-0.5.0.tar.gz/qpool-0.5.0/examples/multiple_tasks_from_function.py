import asyncio
import logging

from wombat.multiprocessing import (
    OrchestratorBuilder,
    loggable,
    task,
)
from wombat.multiprocessing.systems import LoggableSystem
from wombat.multiprocessing.worker import Worker


# 1. Define a generic task action.
def process_data(worker: Worker, data: str) -> str:
    """A simple task that processes some data."""
    processed_data = data.upper()
    worker.log(f"Processed '{data}' into '{processed_data}'", logging.DEBUG)
    return processed_data


# 2. Create multiple TaskDefinitions from the same action using decorators.
#    Each definition can have its own unique set of traits.

# A "verbose" version of the task that logs at INFO level.
verbose_process_data = loggable(log_level=logging.INFO)(task(process_data))

# A "quiet" version of the task that only logs on failure (default behavior).
# Here we just apply the @task decorator. The loggable trait is not needed for default logging.
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
            "Note: You should see INFO logs for 'hello' and 'again', but not for 'world'."
        )


if __name__ == "__main__":
    asyncio.run(main())
