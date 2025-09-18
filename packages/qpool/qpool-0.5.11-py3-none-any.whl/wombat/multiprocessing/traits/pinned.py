from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from .models import BaseTrait


class PinnedTrait(BaseTrait):
    """Data component that pins a task to a specific worker name."""

    _decorator_fields: ClassVar[list[str]] = ["worker_name"]
    trait_name: Literal["pinned"] = "pinned"
    worker_name: str = Field(
        ..., description="The name of the worker to pin this task to."
    )
