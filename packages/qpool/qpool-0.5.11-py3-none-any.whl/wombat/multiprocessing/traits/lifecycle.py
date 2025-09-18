from __future__ import annotations

from typing import Literal

from .models import BaseTrait


class QueuedTrait(BaseTrait):
    """Marker trait for a task that has been produced and is waiting to be queued."""

    trait_name: Literal["queued"] = "queued"
