from __future__ import annotations

from typing import Literal

from .models import BaseTrait


# --- Lifecycle Manager Trait ---


class LifecycleManagerTrait(BaseTrait):
    """An internal trait that manages the lifecycle state of a task."""

    trait_name: Literal["lifecycle_manager"] = "lifecycle_manager"


# --- Lifecycle Marker Traits ---


class Created(BaseTrait):
    """Marker trait for a newly created task."""

    trait_name: Literal["created"] = "created"


class QueuedTrait(BaseTrait):
    """Marker trait for a task that has been produced and is waiting to be queued."""

    trait_name: Literal["queued"] = "queued"


class Attempting(BaseTrait):
    """Marker trait for a task that is currently being executed by a worker."""

    trait_name: Literal["attempting"] = "attempting"


class Succeeded(BaseTrait):
    """Marker trait for a task that has successfully completed."""

    trait_name: Literal["succeeded"] = "succeeded"


class Failed(BaseTrait):
    """Marker trait for a task that has terminally failed."""

    trait_name: Literal["failed"] = "failed"


class RetryingTrait(BaseTrait):
    """Marker trait for a task that is being retried."""

    trait_name: Literal["retrying"] = "retrying"


class Expired(BaseTrait):
    """Marker trait for a task that expired before it could be executed."""

    trait_name: Literal["expired"] = "expired"


class Cancelled(BaseTrait):
    """Marker trait for a task that was cancelled."""

    trait_name: Literal["cancelled"] = "cancelled"


class Skipped(BaseTrait):
    """Marker trait for a task that was skipped (e.g., by Debounce)."""

    trait_name: Literal["skipped"] = "skipped"
