from __future__ import annotations

from typing import ClassVar, List, Literal

from pydantic import Field

from .models import BaseTrait


class RequiresPropsTrait(BaseTrait):
    """A trait that specifies which props a task's action requires."""

    _decorator_fields: ClassVar[list[str]] = ["requires_props"]
    trait_name: Literal["requires_props"] = "requires_props"
    requires_props: List[str] = Field(
        default_factory=list,
        description="A list of required props that this trait provides to the task.",
    )
