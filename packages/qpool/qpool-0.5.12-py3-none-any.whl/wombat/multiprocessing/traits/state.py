from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import Field

from .models import BaseTrait


class TaskState(Enum):
    """The core lifecycle state of a task's journey through the execution engine."""

    PENDING = "pending"  # Not yet processed by a worker
    RUNNING = "running"  # Actively being processed by a worker
    RETRYING = "retrying"  # Waiting for a backoff delay to finish
    COMPLETE = "complete"  # The task's lifecycle is finished


class TaskOutcome(Enum):
    """The final, terminal outcome of a task once its lifecycle is COMPLETE."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    EXPIRED = "expired"


class StateTrait(BaseTrait):
    """
    A data component that manages the explicit state machine for a task's lifecycle.
    """

    trait_name: Literal["state"] = "state"
    state: TaskState = TaskState.PENDING
    outcome: Optional[TaskOutcome] = None
    reason: Optional[str] = Field(
        default=None,
        description="A machine-readable reason for the outcome (e.g., an exception string).",
    )
