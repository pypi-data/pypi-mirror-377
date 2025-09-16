from __future__ import annotations

from datetime import datetime, timedelta
from typing import ClassVar, Literal, Optional

from pydantic import Field, model_validator

from .models import BaseTrait, utc_datetime


class ExpirableTrait(BaseTrait):
    """Data component that adds expiration behavior to a task."""

    _decorator_fields: ClassVar[list[str]] = ["expires_after", "expires_at"]
    trait_name: Literal["expirable"] = "expirable"
    created_at: datetime = Field(default_factory=utc_datetime, exclude=True)
    expires_at: Optional[datetime] = Field(
        default=None, description="The UTC timestamp when the task expires."
    )
    expires_after: Optional[timedelta] = Field(
        default=None,
        description="The duration after creation when the task expires.",
        exclude=True,
    )

    @model_validator(mode="after")
    def set_expires_at_from_duration(self) -> "ExpirableTrait":
        if self.expires_after and self.expires_at:
            raise ValueError("Provide 'expires_at' or 'expires_after', not both.")
        if self.expires_after:
            self.expires_at = self.created_at + self.expires_after
        return self
