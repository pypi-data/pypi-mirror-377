# File: src/wombat/multiprocessing/models.py
"""This file contains the models that we composite to represent our Tasks and their behaviors."""

from __future__ import annotations

from contextlib import AsyncExitStack
from datetime import UTC, datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
)
from uuid import uuid4

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from pydantic_partial import create_partial_model


class TaskDefinition(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    action: Callable
    action_name: str
    traits: list[BaseTrait] = Field(default_factory=list)

    def with_traits(self, traits: list[BaseTrait]) -> "TaskDefinition":
        """Returns a new TaskDefinition with additional traits."""
        # Create a new instance to ensure immutability
        new_def = self.model_copy(deep=True)
        new_def.traits.extend(traits)
        return new_def

    def __call__(self, *args: Any, **kwargs: Any) -> "Task":
        """Creates a Task instance from this definition."""
        all_trait_fields = set()
        for trait in self.traits:
            all_trait_fields.update(trait.model_fields.keys())

        task_model_fields = Task.model_fields.keys()

        model_kwargs = {k: v for k, v in kwargs.items() if k in task_model_fields}
        action_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in task_model_fields and k not in all_trait_fields
        }

        # Deep copy traits from definition to instance
        instantiated_traits = [t.model_copy(deep=True) for t in self.traits]

        # Update trait instances with values from kwargs
        for trait in instantiated_traits:
            for field_name in trait.model_fields:
                if field_name in kwargs:
                    setattr(trait, field_name, kwargs[field_name])

        task_data = {
            "action": self.action_name,
            "args": list(args),
            "kwargs": action_kwargs,
            "traits": instantiated_traits,
            **model_kwargs,
        }

        # Add default traits for accounting and lifecycle management.
        from wombat.multiprocessing.traits.accounting import (
            AccountingTrait,
            UncountedTrait,
        )
        from wombat.multiprocessing.traits.lifecycle import Created, LifecycleManagerTrait

        task_data["traits"].extend(
            [UncountedTrait(), AccountingTrait(), Created(), LifecycleManagerTrait()]
        )

        # We can't use create_with_traits because it expects dicts for traits,
        # and we already have instances. model_validate is correct.
        return Task.model_validate(task_data)


def utc_datetime() -> datetime:
    """Return the current time with UTC timezone."""
    return datetime.now(UTC)


if TYPE_CHECKING:
    pass


class Prop(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    initializer: Any | Callable[..., Any] = Field(
        description="The function that initializes the prop. MUST BE SERIALIZABLE."
    )
    init_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments to pass to the initializer.",
    )
    instance: Any = Field(
        description="The resolved instance of the prop.", default=None
    )
    exit_stack: Optional[AsyncExitStack] = Field(
        description="The exit stack managing the prop's context.", default=None
    )
    use_context_manager: bool = Field(
        description="Whether the prop should be used as a context manager.",
        default=True,
    )


UninitializedProp = create_partial_model(Prop, "instance")


class PropConfig(BaseModel):
    """Configuration for a single Prop, using a string path for the initializer."""

    initializer_path: str
    use_context_manager: bool = True


class CountingRule(BaseModel):
    """A declarative rule for the Accounting trait to process."""

    counter_name: str
    on_event: Literal["received", "success", "failure", "retry"]


class BaseTrait(BaseModel):
    """Base class for all task traits, defining the lifecycle hook interface."""

    _decorator_fields: ClassVar[list[str]] = []

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    counting_rules: Optional[List[CountingRule]] = Field(
        default=None,
        description="A list of declarative rules for the Accounting trait to process.",
    )
    requires_traits: Optional[list[str]] = None
    depends_on: Optional[list[str]] = Field(
        default=None,
        description=(
            "A list of trait names that this trait must execute after. For traits at the "
            "same dependency level, the final execution order is determined by the "
            "application order of their decorators (from bottom to top in the source file)."
        ),
    )
    requires_props: Optional[list[str]] = Field(
        default=None,
        description="A list of required props that the trait expects to be passed to it.",
    )
    forbids_traits: Optional[list[str]] = Field(
        default=None,
        description="A list of trait names that cannot be present on the same task.",
    )
    include_all_props: bool = Field(
        default=False,
        description="Whether to include all props in the kwargs passed to the task.",
    )

    # This class is now a pure data container. All logic is in Systems.


class Sentinel(BaseModel):
    """
    A base model for sentinel values passed through IPC queues.

    This provides a common structure for special messages that are not standard
    tasks or results, such as the End-Of-Queue (EOQ) signal.
    """

    sentinel: str


class Task(BaseModel):
    """The core task model, using composition for all behaviors."""

    model_config: ConfigDict = ConfigDict(extra="forbid")
    id: UUID4 = Field(default_factory=lambda: uuid4())
    action: str = Field(
        ...,
        description="The action to be performed by the task. Expected to map to a key in the Workers Action dictionary.",
    )
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    metadata: Optional[dict[str, Any]] = None
    traits: list[Any] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_and_sort_traits(self) -> "Task":
        """
        Ensures trait dependencies are met and sorts traits topologically.
        """
        if not self.traits:
            return self

        # De-duplicate traits by name, keeping the first instance encountered.
        # This prevents default traits from overwriting configured ones.
        unique_traits: list[Any] = []
        seen_trait_names: set[str] = set()
        for trait in self.traits:
            # getattr is used for safety, though trait_name should always exist.
            trait_name = getattr(trait, "trait_name", None)
            if trait_name not in seen_trait_names:
                unique_traits.append(trait)
                if trait_name:
                    seen_trait_names.add(trait_name)
        self.traits = unique_traits

        # Iteratively apply `forbids_traits` rules until the list of traits stabilizes.
        # This correctly handles chains of forbidden traits.
        while True:
            initial_trait_names = {getattr(t, "trait_name", None) for t in self.traits}
            forbidden_by_active_traits = set()
            for trait in self.traits:
                if trait.forbids_traits:
                    forbidden_by_active_traits.update(trait.forbids_traits)

            if not forbidden_by_active_traits:
                break  # No active rules, we are stable.

            self.traits = [
                t
                for t in self.traits
                if getattr(t, "trait_name", None) not in forbidden_by_active_traits
            ]

            final_trait_names = {getattr(t, "trait_name", None) for t in self.traits}

            if initial_trait_names == final_trait_names:
                break  # The list of traits is stable.

        trait_map = {trait.trait_name: trait for trait in self.traits}
        present_names = set(trait_map.keys())

        adj = {name: [] for name in present_names}
        in_degree = {name: 0 for name in present_names}

        for name, trait in trait_map.items():
            if hasattr(trait, "requires_traits") and trait.requires_traits:
                required = set(trait.requires_traits)
                if not required.issubset(present_names):
                    raise ValueError(
                        f"Task '{self.action}' trait '{name}' is missing required traits: {required - present_names}"
                    )

            if trait.depends_on:
                for dep in trait.depends_on:
                    if dep not in present_names:
                        raise ValueError(
                            f"Task '{self.action}' trait '{name}' has unmet dependency: '{dep}'"
                        )
                    adj[dep].append(name)
                    in_degree[name] += 1

        order_map = {trait.trait_name: i for i, trait in enumerate(self.traits)}
        queue = sorted(
            [n for n in present_names if in_degree[n] == 0], key=order_map.get
        )

        sorted_traits = []
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            sorted_traits.append(trait_map[u])

            for v in sorted(adj[u], key=order_map.get):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(sorted_traits) != len(present_names):
            raise ValueError(
                f"Cycle detected in trait dependencies for task '{self.action}'."
            )

        self.traits = sorted_traits
        return self

    @classmethod
    def create_with_traits(
        cls, data: dict[str, Any], trait_registry: dict[str, Type[BaseTrait]]
    ) -> "Task":
        """
        Factory method to create a Task instance, ensuring that any trait
        definitions in the input data are correctly instantiated.
        """
        if isinstance(data, dict):
            import cloudpickle as pickle

            instantiated_traits = []
            for trait_data in data.get("traits", []):
                if isinstance(trait_data, BaseTrait):
                    instantiated_traits.append(trait_data)
                elif isinstance(trait_data, dict):
                    # Unpickle any fields that were pickled by the custom encoder.
                    for key, value in trait_data.items():
                        if isinstance(value, dict) and value.get("__pickle__"):
                            trait_data[key] = pickle.loads(value["data"])
                    trait_name = trait_data.get("trait_name")
                    if trait_registry and trait_name in trait_registry:
                        TraitModel = trait_registry[trait_name]
                        instantiated_traits.append(TraitModel(**trait_data))
                    else:
                        # An unknown trait dictionary indicates a potential configuration mismatch
                        # between the sender and receiver. Instead of silently dropping it,
                        # we must raise an error to ensure data integrity.
                        raise TypeError(
                            f"Unknown trait '{trait_name}' encountered during task creation. "
                            "Ensure this trait is registered on the receiving end."
                        )
                else:
                    instantiated_traits.append(trait_data)
            data["traits"] = instantiated_traits
        return cls.model_validate(data)

    def add_trait(self, trait: BaseTrait):
        """Adds a trait to the task and re-sorts the trait list."""
        self.traits.append(trait)
        self._validate_and_sort_traits()

    def remove_traits_by_type(self, *trait_types: Type[BaseTrait]):
        """Removes all traits of the given type(s) from the task."""
        new_traits = []
        for t in self.traits:
            is_instance = isinstance(t, trait_types)
            if not is_instance:
                new_traits.append(t)
        self.traits = new_traits
        self._validate_and_sort_traits()

    def replace_trait(self, trait: BaseTrait):
        """
        Replaces a trait of the same type with the provided instance.

        This is useful for traits that manage their own state (like `Retryable`)
        and need to update themselves on the task object.
        """
        trait_type = type(trait)
        self.traits = [t for t in self.traits if not isinstance(t, trait_type)]
        self.traits.append(trait)
        self._validate_and_sort_traits()


class TaskResult(BaseModel):
    """A lightweight model for returning task results from a worker."""

    model_config: ConfigDict = ConfigDict(extra="forbid")
    task_id: UUID4
    action: str
    result: Any = None
    metadata: Optional[dict[str, Any]] = None
    traits: list[Any] = Field(default_factory=list)


class EOQ(Sentinel):
    """A sentinel object indicating that a queue will receive no more items."""

    sentinel: str = "EOQ"


T = TypeVar("T")


# Late imports to resolve forward references and avoid circular dependencies.


ProgressState = Any
