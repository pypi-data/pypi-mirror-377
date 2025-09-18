from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar, Literal

from pydantic import Field


from .models import BaseTrait

if TYPE_CHECKING:
    pass


class RateLimitTrait(BaseTrait):
    """
    Data component that limits the execution frequency of tasks within a group.
    """

    _decorator_fields: ClassVar[list[str]] = ["limit", "period", "group"]
    trait_name: Literal["rate_limit"] = "rate_limit"
    limit: int = Field(
        gt=0, description="The maximum number of tasks to execute within the period."
    )
    period: timedelta = Field(description="The time window for the rate limit.")
    group: str = Field(
        description="A unique key to group different task types under the same rate limit."
    )

