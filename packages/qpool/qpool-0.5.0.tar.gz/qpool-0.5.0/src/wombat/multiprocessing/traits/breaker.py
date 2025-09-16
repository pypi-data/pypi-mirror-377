from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Literal, Optional

from pydantic import Field


from .models import BaseTrait

if TYPE_CHECKING:
    pass


class CircuitBreakerState(Enum):
    """Enumeration of possible states for a circuit breaker."""

    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2


class BreakerTrait(BaseTrait):
    """
    Data component for the Circuit Breaker pattern. Requires 'breaker_lock'
    and 'breaker_states' Props, which are auto-injected by the Orchestrator.
    """

    _decorator_fields: ClassVar[list[str]] = [
        "failure_threshold",
        "recovery_timeout",
        "group",
    ]
    trait_name: Literal["breaker"] = "breaker"
    failure_threshold: int = Field(
        gt=0, default=5, description="Number of failures to open the circuit."
    )
    recovery_timeout: float = Field(
        gt=0.0,
        default=30.0,
        description="Seconds to wait before moving from OPEN to HALF_OPEN.",
    )
    group: Optional[str] = Field(
        default=None,
        description="An optional key to group different task types under the same circuit breaker.",
    )

