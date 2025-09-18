from __future__ import annotations

from typing import ClassVar, List, Literal

from pydantic import Field

from .models import BaseTrait


class TaggedTrait(BaseTrait):
    """A data component to apply arbitrary string tags to a task."""

    _decorator_fields: ClassVar[list[str]] = ["tags"]
    trait_name: Literal["tagged"] = "tagged"
    tags: List[str] = Field(default_factory=list, description="A list of tags.")
