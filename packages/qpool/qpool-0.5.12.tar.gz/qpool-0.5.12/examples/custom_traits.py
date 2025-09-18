import asyncio
import logging
from typing import Any, Literal

from typing import ClassVar, List, Type

from wombat.multiprocessing import (
    OrchestratorBuilder,
    create_trait_decorator,
    task,
)
from wombat.multiprocessing.systems import BaseSystem, priority
from wombat.multiprocessing.traits.models import BaseTrait, Task
from wombat.multiprocessing.worker import Worker


# 1. Define your custom data-only trait.
class AuditableTrait(BaseTrait):
    """A data component for a custom trait to log a message."""

    trait_name: Literal["auditable"] = "auditable"
    audit_message: str


# 2. Define the logic in a stateless System.
class AuditableSystem(BaseSystem):
    """A system that implements the logic for the AuditableTrait."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [AuditableTrait]

    @staticmethod
    @priority(500)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        auditable_trait = next(
            (t for t in task.traits if isinstance(t, AuditableTrait)), None
        )
        if auditable_trait:
            worker.log(
                f"AUDIT START: {auditable_trait.audit_message} for task {task.id}",
                logging.INFO,
            )
        return True, task

    @staticmethod
    @priority(500)
    async def on_task_success(task: "Task", worker: "Worker", result: Any):
        if any(isinstance(t, AuditableTrait) for t in task.traits):
            worker.log(
                f"AUDIT END: Task {task.id} completed successfully.", logging.INFO
            )


# 3. Create a decorator for your custom trait using the factory.
auditable = create_trait_decorator(AuditableTrait)


# 4. Define the task action and apply decorators to create the TaskDefinition.
@auditable(audit_message="Performing important calculation")
@task
def add_numbers(worker: Worker, x: int, y: int) -> int:
    """A simple task that adds two numbers."""
    return x + y


# 5. Use the Orchestrator to run the task, registering the new System.
async def main():
    # Configure logging to see the audit messages in the console.
    logging_config = {"to_console": True, "level": logging.INFO}

    async with (
        OrchestratorBuilder()
        .with_workers(num_workers=2)
        .with_actions([add_numbers])
        .with_logging(logging_config)
        .with_systems([AuditableSystem])
        .build()
    ) as orchestrator:
        # Create a task instance from the decorated function.
        task_instance = add_numbers(5, 10)

        # Add the task to the pool.
        await orchestrator.add_task(task_instance)

        # Wait for the task to complete and get the results.
        await orchestrator.finish_tasks()
        list(orchestrator.get_results())


if __name__ == "__main__":
    asyncio.run(main())
