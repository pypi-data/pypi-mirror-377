import asyncio
import logging
from typing import ClassVar, List, Literal, Type

from wombat.multiprocessing import (
    OrchestratorBuilder,
    create_trait_decorator,
    task,
)
from wombat.multiprocessing.systems import BaseSystem, priority
from wombat.multiprocessing.traits.models import BaseTrait, Task
from wombat.multiprocessing.worker import Worker


# 1. Define a custom data-only trait that takes no arguments.
class NoArgumentTrait(BaseTrait):
    """A simple marker trait that doesn't need any configuration."""

    trait_name: Literal["no_argument"] = "no_argument"


# 2. Define the logic for the trait in a stateless System.
class NoArgumentSystem(BaseSystem):
    """Implements the logic for NoArgumentTrait."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [NoArgumentTrait]

    @staticmethod
    @priority(500)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        if any(isinstance(t, NoArgumentTrait) for t in task.traits):
            worker.log(f"Executing task {task.id} with NoArgumentTrait.", logging.INFO)
        return True, task


# 3. Use the factory to create a decorator for the trait.
no_argument = create_trait_decorator(NoArgumentTrait)


# 4. Apply the decorator to a task action. Because it takes no arguments,
#    it can be used without parentheses (`@no_argument`).
@no_argument
@task
def my_task(worker: Worker):
    worker.log(f"my_task is running on {worker.identity.name}", logging.INFO)
    return "done"


async def main():
    logging_config = {"to_console": True, "level": logging.INFO}

    async with (
        OrchestratorBuilder()
        .with_workers(num_workers=1)
        .with_actions([my_task])
        .with_logging(logging_config)
        .with_systems([NoArgumentSystem])  # Register the system
        .build()
    ) as orchestrator:
        await orchestrator.add_task(my_task())
        await orchestrator.finish_tasks()
        list(orchestrator.get_results())
        print(
            "\nNote: You should see a log message from NoArgumentSystem "
            "before the task executes."
        )


if __name__ == "__main__":
    asyncio.run(main())
