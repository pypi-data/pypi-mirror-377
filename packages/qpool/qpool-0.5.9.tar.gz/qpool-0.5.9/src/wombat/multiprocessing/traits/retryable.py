from __future__ import annotations

from typing import Any, ClassVar, Literal, Optional

from pydantic import Field, model_validator

from .models import BaseTrait


class RetryableTrait(BaseTrait):
    """Data component for retry behavior."""

    _decorator_fields: ClassVar[list[str]] = [
        "max_tries",
        "initial_delay",
        "max_delay",
        "backoff_strategy",
        "backoff_multiplier",
        "backoff_function",
    ]
    trait_name: Literal["retryable"] = "retryable"
    tries: int = Field(
        ge=0,
        default=0,
        description="The number of times the task has been attempted after the initial one.",
    )
    max_tries: int = Field(
        ge=0,
        default=3,
        description="The maximum number of times the task can be retried.",
    )
    initial_delay: float = Field(
        ge=0.0, default=2, description="The initial delay before the first retry."
    )
    max_delay: float = Field(
        ge=0.0, default=60.0, description="The maximum delay between retries."
    )
    backoff_strategy: Literal["exponential", "linear", "custom"] = Field(
        default="exponential",
        description="The backoff strategy to use for retries ('exponential', 'linear', or 'custom').",
    )
    backoff_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        description="The multiplier to use for exponential backoff. Must be >= 1.",
    )
    backoff_function: Optional[Any] = Field(
        default=None,
        description="A custom function to calculate backoff delay. Used when strategy is 'custom'.",
    )

    @model_validator(mode="after")
    def check_custom_backoff_function(self) -> "RetryableTrait":
        if self.backoff_strategy == "custom" and self.backoff_function is None:
            raise ValueError(
                "A 'backoff_function' must be provided when 'backoff_strategy' is 'custom'."
            )
        return self
