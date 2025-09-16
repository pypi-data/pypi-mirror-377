from __future__ import annotations

from typing import ClassVar, List, Literal

from pydantic import Field

from .models import BaseTrait


class ConsumesTrait(BaseTrait):
    """Data component for a task that consumes results from tagged producers."""

    _decorator_fields: ClassVar[list[str]] = ["tags", "batch_size"]
    trait_name: Literal["consumes"] = "consumes"
    tags: List[str] = Field(
        ...,
        description="The list of tags to consume results from. The first tag is the primary grouping key.",
    )
    batch_size: int = Field(
        gt=0,
        description="The number of results to consume before this task is executed.",
    )
