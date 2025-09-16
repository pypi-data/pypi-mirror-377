from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from wombat.multiprocessing.traits.models import BaseTrait, TaskDefinition

# Runtime imports to avoid circular dependencies and for type checking.
from wombat.multiprocessing.traits.models import TaskDefinition

from .accounting import UncountedTrait
from .breaker import BreakerTrait
from .consumes import ConsumesTrait
from .debounce import DebounceTrait
from .delayed import DelayedTrait
from .expirable import ExpirableTrait
from .loggable import LogCarrierTrait, LoggableTrait
from .pinned import PinnedTrait
from .produces import ProducesTrait
from .rate_limit import RateLimitTrait
from .requires_props import RequiresPropsTrait
from .retryable import RetryableTrait
from .tagged import TaggedTrait
from .timeout import TimeoutTrait


def task(func: Callable) -> "TaskDefinition":
    """
    Creates a TaskDefinition from a function.

    This is the entry point for defining tasks with decorators. The returned
    TaskDefinition is a stateless, reusable object that can be configured with
    traits using other decorators stacked on top.
    """
    action_name = f"{func.__module__}.{func.__name__}"
    return TaskDefinition(action=func, action_name=action_name)


def create_trait_decorator(
    trait_class: Type["BaseTrait"],
) -> Callable[..., Callable[["TaskDefinition"], "TaskDefinition"]]:
    """
    A factory that creates a decorator for a specific trait class.

    This is useful for creating simple, stateless decorators for custom traits
    without writing boilerplate code. The resulting decorator accepts arguments
    for the trait's constructor and applies the instantiated trait to a
    TaskDefinition. It handles being used with or without parentheses for
    traits that take no arguments (e.g., `@produces` or `@produces()`).

    Example:
        .. code-block:: python

            # In your traits file
            class MyCustomTrait(BaseTrait):
                trait_name: Literal["my_custom"] = "my_custom"
                my_param: str

            # In your decorators file
            my_custom = create_trait_decorator(MyCustomTrait)

            # In your tasks file
            @my_custom(my_param="some_value")
            @task
            def my_task_action(worker, **kwargs):
                ...
    """

    def trait_decorator_factory(*args, **kwargs):
        # This function handles two cases:
        # 1. @decorator: The decorator is called with the function as the first arg.
        # 2. @decorator(..): The decorator is called with args/kwargs, and returns a function.

        # Check if the first argument is a TaskDefinition and no other args/kwargs are present.
        # This indicates usage like `@produces` instead of `@produces()`.
        is_bare_decorator = (
            len(args) == 1 and not kwargs and isinstance(args[0], TaskDefinition)
        )

        if is_bare_decorator:
            task_def = args[0]
            # Assumes the trait can be initialized with no arguments.
            return task_def.with_traits([trait_class()])

        # Otherwise, we are in the `@decorator(...)` case.
        def decorator(task_def: "TaskDefinition") -> "TaskDefinition":
            if not isinstance(task_def, TaskDefinition):
                raise TypeError(
                    "Trait decorators must be applied to a TaskDefinition (i.e., stacked above @task)."
                )
            return task_def.with_traits([trait_class(*args, **kwargs)])

        return decorator

    return trait_decorator_factory


# Create all the specific trait decorators using the factory.
breaker = create_trait_decorator(BreakerTrait)
consumes = create_trait_decorator(ConsumesTrait)
debounce = create_trait_decorator(DebounceTrait)
delayed = create_trait_decorator(DelayedTrait)
expirable = create_trait_decorator(ExpirableTrait)
loggable = create_trait_decorator(LoggableTrait)
log_carrier = create_trait_decorator(LogCarrierTrait)
pinned = create_trait_decorator(PinnedTrait)
produces = create_trait_decorator(ProducesTrait)
requires_props = create_trait_decorator(RequiresPropsTrait)
rate_limit = create_trait_decorator(RateLimitTrait)
retryable = create_trait_decorator(RetryableTrait)
tagged = create_trait_decorator(TaggedTrait)
timeout = create_trait_decorator(TimeoutTrait)
uncounted = create_trait_decorator(UncountedTrait)

# Add docstrings to the generated decorators for better help() and IDE support.
breaker.__doc__ = "Decorator that adds circuit breaker behavior to a task."
consumes.__doc__ = "Decorator for a task that consumes results from tagged producers."
debounce.__doc__ = (
    "Decorator that prevents duplicate tasks from being executed within a time window."
)
delayed.__doc__ = "Decorator that adds a delay before the task's execution."
expirable.__doc__ = "Decorator that adds expiration behavior to a task."
loggable.__doc__ = "Decorator that adds logging behavior to a task."
log_carrier.__doc__ = (
    "Decorator for a task that MUST NEVER generate log messages during its execution."
)
pinned.__doc__ = "Decorator that pins a task to a specific worker name."
produces.__doc__ = (
    "Decorator that allows a task to dynamically produce new tasks from its result."
)
requires_props.__doc__ = (
    "Decorator that specifies which props a task's action requires."
)
rate_limit.__doc__ = (
    "Decorator that limits the execution frequency of tasks within a group."
)
retryable.__doc__ = "Decorator that adds retry behavior to a task."
tagged.__doc__ = "Decorator to apply one or more string tags to a task."
timeout.__doc__ = "Decorator that adds a timeout to a task's execution."
uncounted.__doc__ = "Decorator for the `Uncounted` trait. This trait marks a task as new, ensuring it is counted by the progress tracking system."
