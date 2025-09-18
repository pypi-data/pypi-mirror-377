from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from .models import BaseTrait


class DelayedTrait(BaseTrait):
    """Data component that adds a delay before the task's execution."""

    _decorator_fields: ClassVar[list[str]] = ["delay"]
    trait_name: Literal["delayed"] = "delayed"
    delay: float = Field(
        gt=0.0, description="Time in seconds to wait before executing the task."
    )
