from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from .models import BaseTrait


class TimeoutTrait(BaseTrait):
    """Data component that adds a timeout to a task's execution."""

    _decorator_fields: ClassVar[list[str]] = ["timeout"]
    trait_name: Literal["timeout"] = "timeout"
    timeout: float = Field(
        gt=0.0, description="Maximum execution time in seconds for the task."
    )
