from __future__ import annotations

from typing import ClassVar, List, Literal, Optional

from pydantic import Field

from .models import BaseTrait


class ProducesTrait(BaseTrait):
    """
    Data component that allows a task to dynamically produce new tasks from its result.
    """

    _decorator_fields: ClassVar[list[str]] = ["tags"]
    trait_name: Literal["produces"] = "produces"
    tags: Optional[List[str]] = Field(
        default=None,
        description="A list of tags to apply to all produced child tasks.",
    )
