from __future__ import annotations

from typing import Any, ClassVar, Literal, Optional

from .models import BaseTrait


class EvaluatableTrait(BaseTrait):
    """Data component that adds result evaluation to a task."""

    _decorator_fields: ClassVar[list[str]] = ["evaluator"]
    trait_name: Literal["evaluatable"] = "evaluatable"
    evaluator: Optional[Any] = None
