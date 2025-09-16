from __future__ import annotations

import logging
from typing import ClassVar, Literal

from .models import BaseTrait


class LoggableTrait(BaseTrait):
    """Data component that adds logging behavior to a task."""

    _decorator_fields: ClassVar[list[str]] = ["log_level"]
    trait_name: Literal["loggable"] = "loggable"
    log_level: int = logging.INFO


class LogCarrierTrait(BaseTrait):
    """This indicates a task that MUST NEVER generate log messages during it's execution.
    i.e. For when you make a logging task for a failure, and the logging task fails thus causing a logging cycle. This prevents that cycle."""

    trait_name: Literal["log_carrier"] = "log_carrier"
    forbids_traits: list[str] = ["uncounted", "accounting"]
