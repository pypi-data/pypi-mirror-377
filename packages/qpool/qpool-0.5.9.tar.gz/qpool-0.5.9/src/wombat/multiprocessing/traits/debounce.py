from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar, Literal, Optional

from pydantic import Field


from .models import BaseTrait

if TYPE_CHECKING:
    pass


class DebounceTrait(BaseTrait):
    """Data component that prevents duplicate tasks from being executed within a time window."""

    _decorator_fields: ClassVar[list[str]] = ["window", "group"]
    trait_name: Literal["debounce"] = "debounce"
    window: timedelta = Field(
        default=timedelta(seconds=60),
        description="The time window within which duplicate tasks will be skipped.",
    )
    group: Optional[str] = Field(
        default=None,
        description=(
            "An optional key to group different task types for deduplication. When a "
            "group is provided, all tasks within that group are debounced against "
            "each other, regardless of their action or arguments."
        ),
    )

