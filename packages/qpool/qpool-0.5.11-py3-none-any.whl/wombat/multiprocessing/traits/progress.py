from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import Field

from .models import BaseTrait


class Progressable(BaseTrait):
    """Trait that adds progress tracking behavior to a task."""

    _decorator_fields: ClassVar[list[str]] = ["weight"]
    trait_name: Literal["progress"] = "progress"
    weight: int = Field(ge=0, default=1)
