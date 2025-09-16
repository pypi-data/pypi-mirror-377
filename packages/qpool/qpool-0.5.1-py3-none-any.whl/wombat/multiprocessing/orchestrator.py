# File: src/wombat/multiprocessing/orchestrator.py
from __future__ import annotations

import asyncio
import datetime
import json
import logging
import os
import signal
import sys
from collections import defaultdict
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
import inspect
from functools import partial
from multiprocessing import get_context
from multiprocessing.context import BaseContext
from queue import Full
from threading import Lock, Thread
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
)
from uuid import uuid4

import msgpack
from pydantic import BaseModel, ConfigDict, Field, computed_field

from wombat.multiprocessing.errors import WorkerCrashError
from wombat.multiprocessing.ipc.buffer import _HEADER, Buffer, BufferConfig, BufferState
from wombat.multiprocessing.ipc.queues.trait_queue import (
    TraitQueue,
    explicitly_is,
    implicitly_is,
    task_validator,
)
from wombat.multiprocessing.ipc.queues.utilities import (
    drain_queue_non_blocking,
    rehydrate_model_from_dict,
)
from wombat.multiprocessing.ipc.utilities import (
    _resolve_path,
    default_encoder,
    queue_get_async,
)
from wombat.multiprocessing.logging import log_task, setup_logging
from wombat.multiprocessing.progress import ProgressConfig, run_progress
from wombat.multiprocessing.traits.consumes import ConsumesTrait
from wombat.multiprocessing.traits.models import (
    EOQ,
    Prop,
    PropConfig,
    Task,
    TaskDefinition,
    TaskResult,
    UninitializedProp,
)
from wombat.multiprocessing.traits.tagged import TaggedTrait
from wombat.multiprocessing.worker import (
    ProfilingConfig,
    Worker,
    WorkerConfig,
    WorkerIdentityConfig,
    WorkerIPCConfig,
    WorkerLoggingConfig,
    WorkerPerformanceConfig,
    WorkerStatus,
)


class QueueConfig(BaseModel):
    slots: int = 4096
    slot_size: int = 128000


def ResultQueue(context: BaseContext, name: str, joinable: bool = False) -> TraitQueue:
    return TraitQueue(
        context=context,
        name=name,
        joinable=joinable,
        validator=implicitly_is,
        validation_list=[TaskResult, EOQ],
        # Results can be large and numerous; give a larger buffer.
        slots=8192,
        slot_size=1.28e8,
    )


class OrchestratorConfig(BaseModel):
    """
    A declarative configuration for the Orchestrator, suitable for loading from JSON.
    """

    workers: list[WorkerConfig] = Field(default_factory=list)
    logging_configs: list[dict[str, Any]] = Field(default_factory=list)

    @computed_field
    @property
    def num_workers(self) -> int:
        """The total number of task workers."""
        return len(self.workers)

    props: dict[str, PropConfig] = Field(default_factory=dict)

    # Behavior/Feature flags
    progress: ProgressConfig = Field(default_factory=ProgressConfig)
    buffer: BufferConfig = Field(default_factory=BufferConfig)
    profiling: ProfilingConfig = Field(default_factory=ProfilingConfig)

    result_queue_config: QueueConfig = Field(default_factory=QueueConfig)
    requeue_queue_config: QueueConfig = Field(default_factory=QueueConfig)

    # Extensibility
    extensions: list[str] = Field(default_factory=list)

    # Performance tuning
    orchestrator_thread_pool_size: Optional[int] = None

    @classmethod
    def from_json(cls, path: str) -> "OrchestratorConfig":
        """Loads orchestrator configuration from a JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)


class OrchestratorBuilder:
    """
    A fluent builder for creating and configuring an `Orchestrator`.

    This class provides a step-by-step API for setting up workers, registering
    task actions, configuring props, and enabling features like logging and
    progress bars.
    """

    def __init__(self):
        self._worker_configs: list[dict[str, Any]] = []
        self._registered_actions: list["TaskDefinition"] = []
        self.props: dict[str, Any] = {}
        self._show_progress: bool = False
        self._systems: list[Any] = []
        self.metrics: Mapping | None = None
        self._profiling_enabled: bool = False
        self._profiling_to_console: bool = True
        self._no_logging: bool = False
        self._batch_config: BufferConfig = BufferConfig()
        self._orchestrator_thread_pool_size: int | None = None
        self._result_queue_config: Optional[QueueConfig] = None
        self._requeue_queue_config: Optional[QueueConfig] = None
        self._resources_to_cleanup: list[Any] = []
        self.context = None

    def without_logging(self) -> "OrchestratorBuilder":
        """Disables the default logger."""
        self._no_logging = True
        return self

    def with_metrics(self, capture_dict: Mapping | None) -> "OrchestratorBuilder":
        """
        Provides a shared dictionary to capture the final state of the accounting.
        """
        self.metrics = capture_dict
        return self

    def register_resource_for_cleanup(self, resource: Any):
        """Registers a shared resource that requires explicit cleanup on shutdown."""
        self._resources_to_cleanup.append(resource)

    def add_worker(
        self,
        props: dict[str, Prop] | None = None,
        max_concurrent_tasks: int | None = None,
        thread_pool_size: int | None = None,
        loop_timeout: float | None = None,
    ) -> "OrchestratorBuilder":
        """Adds a worker with a specific configuration."""
        worker_spec = {
            "props": props if props is not None else {},
            "max_concurrent_tasks": max_concurrent_tasks,
            "thread_pool_size": thread_pool_size,
            "loop_timeout": loop_timeout,
        }
        self._worker_configs.append(worker_spec)
        return self

    def with_workers(
        self,
        num_workers: int,
        max_concurrent_tasks: int | None = None,
        thread_pool_size: int | None = None,
        loop_timeout: float | None = None,
    ) -> "OrchestratorBuilder":
        for _ in range(num_workers):
            self.add_worker(
                max_concurrent_tasks=max_concurrent_tasks,
                thread_pool_size=thread_pool_size,
                loop_timeout=loop_timeout,
            )
        return self

    def add_prop(self, name: str, prop: Prop) -> "OrchestratorBuilder":
        """Adds a single shared prop to the orchestrator configuration."""
        self.props[name] = prop
        return self

    def with_props(self, props: dict[str, Any]) -> "OrchestratorBuilder":
        self.props.update(props if props is not None else {})
        return self

    def add_logger(self, logging_config: dict[str, Any]) -> "OrchestratorBuilder":
        """Adds a worker dedicated to logging."""
        self._worker_configs.append(
            {
                "is_log_worker": True,
                "logging_config": logging_config,
            }
        )
        return self

    def with_logging(
        self, logging_config: dict[str, Any] | None
    ) -> "OrchestratorBuilder":
        if logging_config is not None:
            self.add_logger(logging_config)
        return self

    def with_progress_bar(self, show: bool = True) -> "OrchestratorBuilder":
        self._show_progress = show
        return self

    def with_batch_config(self, config: BufferConfig) -> "OrchestratorBuilder":
        """Sets the configuration for each worker's shared memory batch buffer."""
        self._batch_config = config
        return self

    def with_profiling(
        self, enabled: bool = True, to_console: bool = True
    ) -> "OrchestratorBuilder":
        """Enables line-profiling for each worker."""
        self._profiling_enabled = enabled
        self._profiling_to_console = to_console
        return self

    def with_result_queue_config(
        self, slots: int, slot_size: int
    ) -> "OrchestratorBuilder":
        """Sets the configuration for the result queue."""
        self._result_queue_config = QueueConfig(slots=slots, slot_size=slot_size)
        return self

    def with_requeue_queue_config(
        self, slots: int, slot_size: int
    ) -> "OrchestratorBuilder":
        """Sets the configuration for the requeue queue."""
        self._requeue_queue_config = QueueConfig(slots=slots, slot_size=slot_size)
        return self

    def with_orchestrator_thread_pool_size(self, size: int) -> "OrchestratorBuilder":
        """Sets the size of the orchestrator's thread pool for async executors."""
        self._orchestrator_thread_pool_size = size
        return self

    def with_actions(self, actions: list["TaskDefinition"]) -> "OrchestratorBuilder":
        """Registers task definitions with the orchestrator."""
        self._registered_actions.extend(actions)
        return self

    def with_systems(self, systems: list[Any]) -> "OrchestratorBuilder":
        """Registers System classes with the orchestrator."""
        self._systems.extend(systems)
        return self

    def from_config(self, config: OrchestratorConfig) -> "OrchestratorBuilder":
        """Configures the builder from an OrchestratorConfig object."""
        self.with_progress_bar(config.progress.enabled)
        if config.orchestrator_thread_pool_size is not None:
            self.with_orchestrator_thread_pool_size(
                config.orchestrator_thread_pool_size
            )
        for logging_config in config.logging_configs:
            self.add_logger(logging_config)

        # Resolve global props from PropConfig
        global_resolved_props = {}
        for name, prop_config in config.props.items():
            initializer = _resolve_path(prop_config.initializer_path)
            global_resolved_props[name] = Prop(
                initializer=initializer,
                use_context_manager=prop_config.use_context_manager,
            )
        self.with_props(global_resolved_props)

        # Add workers based on the declarative list
        for worker_config in config.workers:
            resolved_props = {}
            for name, prop_config in worker_config.props.items():
                initializer = _resolve_path(prop_config.initializer_path)
                resolved_props[name] = Prop(
                    initializer=initializer,
                    use_context_manager=prop_config.use_context_manager,
                )

            # TODO: The declarative config for actions is incompatible with the fluent API.
            # This part of `from_config` is now a no-op. A new declarative format is needed.
            self.add_worker(
                props=resolved_props,
                max_concurrent_tasks=worker_config.max_concurrent_tasks,
                thread_pool_size=worker_config.thread_pool_size,
                loop_timeout=worker_config.loop_timeout,
            )

        # TODO: A declarative way to register systems is needed.
        # The `extensions` field in the config is now a no-op.
        self.with_profiling(
            enabled=config.profiling.enabled, to_console=config.profiling.to_console
        )

        self.with_batch_config(config.buffer)

        return self

    def _run_trait_build_hooks(self, actions: dict[str, Callable]):
        # This is now handled directly in the build() method.
        pass

        # This has been moved up to build()

    def build(self) -> Orchestrator:
        """
        Constructs and returns an `Orchestrator` instance based on the configuration.

        This method consolidates all the provided settings, runs the `before_build`
        hooks for all registered traits to auto-provision necessary resources, sets
        up all IPC mechanisms (queues, buffers, locks), and initializes the
        `Worker` objects.

        Returns:
            A fully configured `Orchestrator` ready to be started.
        """
        self.context = get_context("spawn")
        context = self.context
        orchestrator_thread_pool_size = self._orchestrator_thread_pool_size or 2
        num_task_workers = sum(
            1 for spec in self._worker_configs if not spec.get("is_log_worker")
        )

        from wombat.multiprocessing.systems import (
            AccountingSystem,
            LifecycleSystem,
            PinnedSystem,
            RequiresPropsSystem,
        )

        # --- System and Trait Registry Construction ---
        all_trait_classes = set()
        system_registry: dict[str, list[Callable]] = {}
        orchestrator_system_registry: dict[str, list[Callable]] = {}

        # Add default systems required for core functionality.
        default_systems = {
            LifecycleSystem,
            AccountingSystem,
            RequiresPropsSystem,
            PinnedSystem,
        }
        all_systems = set(self._systems) | default_systems

        # Sort systems alphabetically to ensure a deterministic hook order for
        # hooks with the same priority.
        sorted_systems = sorted(all_systems, key=lambda s: s.__name__)

        WORKER_LIFECYCLE_HOOKS = [
            "on_worker_startup",
            "on_task_attempt",
            "before_task_execution",
            "before_prepare_arguments",
            "on_task_success",
            "on_task_failure",
            "on_task_cancelled",
            "on_task_terminal_failure",
            "should_log_failure",
            "on_task_received",
            "around_task_execution",
        ]
        ORCHESTRATOR_LIFECYCLE_HOOKS = [
            "on_task_routed",
            "should_suppress_result",
            "on_task_requeued",
            "on_task_submitted",
        ]

        for system_class in sorted_systems:
            # 1. Collect required traits from all systems.
            all_trait_classes.update(getattr(system_class, "required_traits", []))

            # 2. Build the system registry for workers.
            for hook_name in WORKER_LIFECYCLE_HOOKS:
                if hasattr(system_class, hook_name):
                    hook_func = getattr(system_class, hook_name)
                    if inspect.isfunction(hook_func):  # Catches staticmethods
                        priority = getattr(hook_func, "_hook_priority", 500)
                        system_registry.setdefault(hook_name, []).append(
                            (priority, hook_func)
                        )

            # 3. Build the system registry for the orchestrator.
            for hook_name in ORCHESTRATOR_LIFECYCLE_HOOKS:
                if hasattr(system_class, hook_name):
                    hook_func = getattr(system_class, hook_name)
                    if inspect.isfunction(hook_func):  # Catches staticmethods
                        priority = getattr(hook_func, "_hook_priority", 500)
                        orchestrator_system_registry.setdefault(hook_name, []).append(
                            (priority, hook_func)
                        )

        # After collecting all hooks, sort them by priority.
        for hook_name, hooks in system_registry.items():
            hooks.sort(key=lambda item: item[0])
            system_registry[hook_name] = [func for _, func in hooks]

        for hook_name, hooks in orchestrator_system_registry.items():
            hooks.sort(key=lambda item: item[0])
            orchestrator_system_registry[hook_name] = [func for _, func in hooks]

        all_actions = {
            action.action_name: action for action in self._registered_actions
        }

        # The log_task is an internal detail and should always be available if logging is used.
        if not self._no_logging:
            all_actions[log_task.action_name] = log_task

        # Discover all traits from actions to build the complete map.
        consumer_templates = []
        for action in all_actions.values():
            all_trait_classes.update(type(t) for t in action.traits)
            if any(isinstance(t, ConsumesTrait) for t in action.traits):
                consumer_templates.append(action)

        # Use a hook to discover dependent traits from systems.
        discovered_dependents = set()
        for system_class in all_systems:
            if hasattr(system_class, "get_dependent_traits"):
                discovered_dependents.update(system_class.get_dependent_traits())
        all_trait_classes.update(discovered_dependents)

        trait_registry = {}
        for trait_cls in all_trait_classes:
            # Get the trait_name from the model's field definition, which is
            # more robust than instantiating the trait.
            if (
                hasattr(trait_cls, "model_fields")
                and "trait_name" in trait_cls.model_fields
            ):
                trait_name = trait_cls.model_fields["trait_name"].default
                if trait_name:
                    trait_registry[trait_name] = trait_cls

        # Run system build hooks.
        sorted_systems = sorted(all_systems, key=lambda s: s.__name__)
        for system_class in sorted_systems:
            if hasattr(system_class, "before_build"):
                system_class.before_build(self, all_actions)

        # Trait build hooks are now handled by systems.

        progress_ipc = None
        if self._show_progress:
            # The accounting store is guaranteed to exist by the hook system.
            progress_ipc = {
                "accounting_store": self.props["accounting_store"].initializer,
                "stop_event": context.Event(),
                "update_event": context.Event(),
            }

        init_props = {
            "props": self.props,
            "actions": all_actions,
        }

        # Batch buffers replace the central task queue.
        log_workers_spec = [
            spec for spec in self._worker_configs if spec.get("is_log_worker")
        ]
        num_log_workers = len(log_workers_spec)
        log_batch_buffers = [
            Buffer(context=context, size=self._batch_config.size, create=True)
            for _ in range(num_log_workers)
        ]

        batch_buffers = [
            Buffer(context=context, size=self._batch_config.size, create=True)
            for _ in range(num_task_workers)
        ]

        queues: dict[str, TraitQueue] = {}
        requeue_config = self._requeue_queue_config or QueueConfig()
        queues["requeue"] = TraitQueue(
            context=context,
            name="central_requeue",
            joinable=False,
            slots=requeue_config.slots,
            slot_size=requeue_config.slot_size,
        )

        # If no log workers are configured, add one with a default config for back-compat.
        if (
            not any(c.get("is_log_worker") for c in self._worker_configs)
            and not self._no_logging
        ):
            self.add_logger({})

        result_config = self._result_queue_config or QueueConfig()
        result_queue_validation_list = [TaskResult, EOQ]
        queues["result"] = TraitQueue(
            context=context,
            name="results",
            joinable=False,
            validator=explicitly_is,
            validation_list=result_queue_validation_list,
            slots=result_config.slots,
            slot_size=result_config.slot_size,
        )

        workers = []
        worker_control_queues = {}

        profiling_dir = None
        if self._profiling_enabled:
            timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
            profiling_dir = os.path.join("profiles", timestamp)
            os.makedirs(profiling_dir, exist_ok=True)

        task_worker_idx = 0
        log_worker_idx = 0
        for i, worker_spec in enumerate(self._worker_configs):
            is_log_worker = worker_spec.get("is_log_worker", False)

            worker_id = uuid4()
            worker_name = (
                f"log-worker-{log_worker_idx}"
                if is_log_worker
                else f"worker-{task_worker_idx}"
            )
            control_queue_name = f"control-{worker_id}"
            worker_status = context.Value("i", WorkerStatus.CREATED.value)
            worker_control_queues[control_queue_name] = TraitQueue(
                context=context,
                name=control_queue_name,
                joinable=True,
                validator=task_validator,
                validation_list=[],
            )

            if is_log_worker:
                worker_actions = {
                    log_task.action_name: all_actions[log_task.action_name]
                }
            else:
                worker_actions = {
                    k: v for k, v in all_actions.items() if k != log_task.action_name
                }

            # Merge global props with worker-specific props. Worker-specific props override global ones.
            worker_props = {**self.props, **worker_spec.get("props", {})}
            if is_log_worker:
                logging_config = worker_spec["logging_config"]
                worker_props["logger"] = UninitializedProp(
                    initializer=setup_logging,
                    init_kwargs=logging_config,
                    use_context_manager=False,
                )

            worker_max_concurrent_tasks = worker_spec.get("max_concurrent_tasks")
            worker_thread_pool_size = worker_spec.get("thread_pool_size") or 2
            worker_loop_timeout = worker_spec.get("loop_timeout")
            if worker_loop_timeout is None:
                # This must match the default in `wombat.multiprocessing.models.WorkerConfig`
                worker_loop_timeout = 0.1

            worker_queues = {
                "requeue": queues["requeue"],
                "result": queues["result"],
            }
            if is_log_worker:
                worker_config = WorkerConfig(
                    actions=worker_actions,
                    trait_registry=trait_registry,
                    system_registry=system_registry,
                    props=worker_props,
                    identity=WorkerIdentityConfig(
                        name=worker_name,
                        id=worker_id,
                        progress_bar_id=-1,
                    ),
                    performance=WorkerPerformanceConfig(
                        max_concurrent_tasks=None,
                        thread_pool_size=worker_thread_pool_size,
                    ),
                    ipc=WorkerIPCConfig(
                        context=context,
                        control_queues={
                            "primary": worker_control_queues[control_queue_name]
                        },
                        queues=worker_queues,
                        batch_buffer=log_batch_buffers[log_worker_idx],
                        status=worker_status,
                    ),
                )
                workers.append(Worker(config=worker_config))
                log_worker_idx += 1
            else:
                worker_config = WorkerConfig(
                    actions=worker_actions,
                    trait_registry=trait_registry,
                    system_registry=system_registry,
                    props=worker_props,
                    identity=WorkerIdentityConfig(
                        name=worker_name,
                        id=worker_id,
                        progress_bar_id=task_worker_idx,
                    ),
                    performance=WorkerPerformanceConfig(
                        max_concurrent_tasks=worker_max_concurrent_tasks,
                        thread_pool_size=worker_thread_pool_size,
                        loop_timeout=worker_loop_timeout,
                    ),
                    ipc=WorkerIPCConfig(
                        context=context,
                        control_queues={
                            "primary": worker_control_queues[control_queue_name]
                        },
                        queues=worker_queues,
                        batch_buffer=batch_buffers[task_worker_idx],
                        status=worker_status,
                    ),
                    logging=WorkerLoggingConfig(
                        enabled=not self._no_logging,
                    ),
                    profiling=ProfilingConfig(
                        enabled=self._profiling_enabled,
                        dir=profiling_dir,
                        to_console=self._profiling_to_console,
                    ),
                )
                workers.append(Worker(config=worker_config))
                task_worker_idx += 1

        queues.update(worker_control_queues)

        runtime_config = OrchestratorRuntimeConfig(
            context=context,
            workers=workers,
            batch_buffers=batch_buffers + log_batch_buffers,
            queues=queues,
            progress_ipc=progress_ipc,
            show_progress=self._show_progress,
            init_props=init_props,
            progress_state_capture_dict=self.metrics,
            thread_pool_size=orchestrator_thread_pool_size,
            resources_to_cleanup=self._resources_to_cleanup,
            logging_enabled=not self._no_logging,
            trait_registry=trait_registry,
            orchestrator_system_registry=orchestrator_system_registry,
            consumer_templates=consumer_templates,
        )

        # Run after_build hooks
        for system_class in sorted_systems:
            if hasattr(system_class, "after_build"):
                system_class.after_build(self, all_actions)

        return Orchestrator(config=runtime_config)


class OrchestratorRuntimeConfig(BaseModel):
    """Configuration and resources for an Orchestrator instance."""

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    context: BaseContext
    workers: list[Worker]
    batch_buffers: list[Buffer]
    queues: dict[str, TraitQueue]
    progress_ipc: dict[str, Any] | None
    show_progress: bool
    init_props: dict[str, Any]
    progress_state_capture_dict: Any
    thread_pool_size: int
    resources_to_cleanup: list[Any]
    logging_enabled: bool
    trait_registry: dict[str, Any]
    orchestrator_system_registry: dict[str, Any]
    consumer_templates: list[Any]


class Orchestrator:
    """
    The main coordinator for the Wombat multiprocessing framework.

    The Orchestrator is responsible for:
    - Managing the lifecycle of worker processes.
    - Distributing tasks to workers based on traits like `Pinned`.
    - Collecting results from workers.
    - Handling dynamic task production and retries via a central requeue mechanism.
    - Providing an async interface for adding tasks and waiting for their completion.
    """

    def __init__(self, config: OrchestratorRuntimeConfig):
        # Core components from the builder
        self.context = config.context
        self.workers = config.workers
        self.log_workers = [
            w
            for w in self.workers
            if w.identity.name and "log-worker" in w.identity.name
        ]
        self.batch_buffers = config.batch_buffers
        self.props = config.init_props.get("props", {})
        self._resources_to_cleanup: list[Any] = config.resources_to_cleanup

        # IPC queues
        self.queues = config.queues

        # Feature configurations
        self.logging_enabled = config.logging_enabled
        self.orchestrator_system_registry = config.orchestrator_system_registry
        self.show_progress = config.show_progress
        self.progress_ipc = config.progress_ipc
        self.progress_state_capture_dict = config.progress_state_capture_dict
        self.thread_pool_size = config.thread_pool_size

        # Runtime state for task and result management
        self._results_buffer: list[Task] = []
        self._results_buffer_lock = Lock()

        # Runtime state for asyncio and background tasks
        self.loop: asyncio.AbstractEventLoop | None = None
        self._shutdown_event: asyncio.Event | None = None
        self._worker_crash_event: asyncio.Event | None = None
        self._pid_to_worker_map: dict[int, Worker] = {}
        self._completion_queue: asyncio.Queue | None = None
        self._result_collection_task: asyncio.Task | None = None
        self._requeue_listener_task: asyncio.Task | None = None
        self.progress_thread: Thread | None = None

        # Lifecycle flags
        self.started = False
        self.stopped = False
        self.trait_registry = config.trait_registry

        # Consumer state management
        self._consumer_templates = config.consumer_templates
        self._tagged_results: dict[str, list] = defaultdict(list)
        self._waiting_consumers: dict[str, list[Task]] = defaultdict(list)

        self.log(f"Orchestrator initialized in pid={os.getpid()}", logging.DEBUG)

    async def _check_and_emit_consumers(self, triggered_by_tags: set[str]):
        """Checks if any waiting consumers can be satisfied and emits them."""
        tasks_to_add = []
        for tag in triggered_by_tags:
            while True:
                if not self._waiting_consumers[tag]:
                    break

                consumer_task = self._waiting_consumers[tag][0]
                consumes_trait = next(
                    (t for t in consumer_task.traits if isinstance(t, ConsumesTrait)),
                    None,
                )

                if not consumes_trait:
                    # Should not happen if logic is correct.
                    self._waiting_consumers[tag].pop(0)
                    continue

                if len(self._tagged_results[tag]) >= consumes_trait.batch_size:
                    # We have a complete batch.
                    self._waiting_consumers[tag].pop(0)

                    # Atomically grab the results and update the buffer.
                    results_batch = self._tagged_results[tag][: consumes_trait.batch_size]
                    self._tagged_results[tag] = self._tagged_results[tag][
                        consumes_trait.batch_size :
                    ]

                    consumer_task.kwargs["consumed_results"] = results_batch
                    tasks_to_add.append(consumer_task)
                else:
                    # Not enough results for this consumer yet.
                    break

        if tasks_to_add:
            await self.add_tasks(tasks_to_add, _from_poller=True)

    async def __aenter__(self):
        """Starts workers and returns the orchestrator instance."""
        self.log(f"Entering __aenter__ in pid={os.getpid()}", logging.DEBUG)
        await self._start_workers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures workers are stopped on context exit."""
        if self.started and not self.stopped:
            self.log(f"Entering __aexit__ in pid={os.getpid()}", logging.DEBUG)
            self.log(
                f"Orchestrator shutting down from context exit ({exc_type.__name__ if exc_type else 'normal exit'}).",
                logging.INFO,
            )
            await self._shutdown()

    async def _wait_for_log_workers_to_idle(self):
        """Waits until all log workers report an idle (SLEEPING) status."""
        self.log(
            "Waiting for log workers to become idle before final shutdown.",
            logging.DEBUG,
        )
        while True:
            all_idle = all(
                w.ipc.status.value == WorkerStatus.SLEEPING.value
                for w in self.log_workers
            )
            if all_idle:
                self.log(
                    "All log workers are idle. Proceeding with shutdown.", logging.DEBUG
                )
                break
            await asyncio.sleep(0.01)

    def _handle_sigchld(self):
        """Signal handler for SIGCHLD to detect worker crashes."""
        # This is a signal handler, so it must be synchronous and very fast.
        # We just check for a dead process and set the event. The main async
        # loop will handle the rest.
        for worker in self.workers:
            if not worker._process.is_alive() and not self.stopped:
                if self._worker_crash_event and not self._worker_crash_event.is_set():
                    self._worker_crash_event.set()
                # One is enough to signal a problem.
                break

    async def _collect_results_continuously_async(
        self, num_workers_to_expect: int, completion_queue: asyncio.Queue
    ):
        """Continuously drains the result queue in a dedicated asyncio task."""

        self.log("Result collector task running.", logging.DEBUG)
        eoq_received = 0

        # Create a task that will complete when the orchestrator is shutting down.
        stop_waiter = self.loop.create_task(self._shutdown_event.wait())

        while eoq_received < num_workers_to_expect:
            # Create a task to wait for the next item from the result queue.
            queue_waiter = self.loop.create_task(queue_get_async(self.queues["result"]))

            try:
                # Wait for either the stop signal or a new result.
                done, pending = await asyncio.wait(
                    [stop_waiter, queue_waiter], return_when=asyncio.FIRST_COMPLETED
                )

                if queue_waiter in done:
                    result_data = queue_waiter.result()
                else:
                    # The stop_waiter must be done, so we are shutting down.
                    # Cancel the pending queue waiter and exit the loop.
                    queue_waiter.cancel()
                    self.log("Result collector received stop signal.", logging.INFO)
                    break

                if isinstance(result_data, dict):
                    result_item = rehydrate_model_from_dict(
                        result_data, self.trait_registry
                    )
                else:
                    # This case should not be hit with a properly functioning system.
                    result_item = result_data

                # ResultQueue is non-joinable, so no task_done() is needed.
                if isinstance(result_item, EOQ):
                    eoq_received += 1
                    self.log(
                        f"Received EOQ ({eoq_received}/{num_workers_to_expect}).",
                        logging.DEBUG,
                    )
                else:
                    self.log(
                        f"Collected result for task {result_item.task_id}.",
                        logging.DEBUG,
                    )

                    # The task_store has been removed. A Task object is reconstructed from the
                    # TaskResult and buffered for the user.
                    task_from_result = Task(
                        id=result_item.task_id,
                        action=result_item.action,
                        result=result_item.result,
                        metadata=result_item.metadata,
                        traits=result_item.traits,
                    )
                    task_from_result._validate_and_sort_traits()

                    with self._results_buffer_lock:
                        self._results_buffer.append(task_from_result)

                    tagged_trait = next(
                        (t for t in task_from_result.traits if isinstance(t, TaggedTrait)),
                        None,
                    )
                    if tagged_trait and tagged_trait.tags:
                        affected_tags = set()
                        for tag in tagged_trait.tags:
                            self._tagged_results[tag].append(task_from_result.result)
                            affected_tags.add(tag)

                        if affected_tags:
                            await self._check_and_emit_consumers(affected_tags)

                    await completion_queue.put(None)
            except (EOFError, asyncio.CancelledError):
                self.log(
                    "Result collector task cancelled or queue closed.", logging.INFO
                )
                break
            except Exception as e:
                self.log(f"Result collector encountered an error: {e}", logging.ERROR)
                break

        # Cleanup the stop_waiter task if it's still pending.
        if not stop_waiter.done():
            stop_waiter.cancel()

        self.log("Result collector task loop finished.", logging.DEBUG)
        # After the loop, perform a final drain to catch any stragglers.
        remaining_results = drain_queue_non_blocking(
            self.queues["result"], self.trait_registry
        )
        with self._results_buffer_lock:
            for result_item in remaining_results:
                if isinstance(result_item, EOQ):
                    continue

                if not isinstance(result_item, TaskResult):
                    # Should not happen with the new logic, but handle gracefully.
                    continue

                task_from_result = Task(
                    id=result_item.task_id,
                    action=result_item.action,
                    result=result_item.result,
                    metadata=result_item.metadata,
                    traits=result_item.traits,
                )
                task_from_result._validate_and_sort_traits()
                self._results_buffer.append(task_from_result)
        self.log("Result collector task exiting.", logging.DEBUG)

    async def _requeue_listener_async(self):
        """Listens on the central requeue channel and redistributes tasks."""
        from wombat.multiprocessing.ipc.utilities import queue_get_async

        self.log("Requeue listener task running.", logging.DEBUG)
        stop_waiter = self.loop.create_task(self._shutdown_event.wait())

        while not self._shutdown_event.is_set():
            queue_waiter = self.loop.create_task(
                queue_get_async(self.queues["requeue"])
            )
            try:
                # Wait for either a new task or the stop signal.
                done, _ = await asyncio.wait(
                    [stop_waiter, queue_waiter], return_when=asyncio.FIRST_COMPLETED
                )

                if queue_waiter in done:
                    task_data = queue_waiter.result()
                else:
                    # Stop event was triggered.
                    queue_waiter.cancel()
                    break

                task = Task.create_with_traits(
                    task_data, trait_registry=self.trait_registry
                )
                unhandled_tasks = []
                handled = False
                if "on_task_requeued" in self.orchestrator_system_registry:
                    for system_func in self.orchestrator_system_registry[
                        "on_task_requeued"
                    ]:
                        if await system_func(task, self):
                            handled = True
                            break

                if not handled:
                    unhandled_tasks.append(task)

                if unhandled_tasks:
                    await self.add_tasks(unhandled_tasks, _from_poller=True)

            except asyncio.CancelledError:
                self.log("Requeue listener task cancelled.", logging.INFO)
                if not queue_waiter.done():
                    queue_waiter.cancel()
                break
            except Exception as e:
                self.log(f"Requeue listener encountered an error: {e}", logging.ERROR)
                # Avoid busy-looping on persistent errors.
                await asyncio.sleep(0.1)

        if not stop_waiter.done():
            stop_waiter.cancel()
        self.log("Requeue listener task exiting.", logging.DEBUG)

    def log(self, message: str, level: int) -> None:
        """
        Sends a log message to be processed by a dedicated log worker.

        This prevents logging I/O from blocking the orchestrator's event loop
        or the main application thread.
        """
        if not self.logging_enabled:
            return
        if self.stopped:
            # During shutdown, logging can cause deadlocks if it tries to put
            # to a queue that's being joined.
            return
        if not self.log_workers:
            return

        # Create a proper log_task, similar to how Worker.log does it.
        log_task_item = log_task(message=message, level=level)

        # Send the log task to the central requeue for accounting and dispatch.
        requeue_queue = self.queues.get("requeue")
        if requeue_queue:
            try:
                requeue_queue.put_nowait(log_task_item)
            except Full:
                print(
                    f"CRITICAL: Requeue queue for logging is full. Orchestrator message lost: {message}",
                    file=sys.stderr,
                    flush=True,
                )

    async def _join_or_terminate_process(self, process_owner):
        """Joins a process."""
        await self.loop.run_in_executor(None, process_owner._process.join)
        self.log(f"Process {process_owner.identity.name} has exited.", logging.DEBUG)

    async def _start_workers(self):
        """Starts workers and optionally monitors progress."""
        self.log("Entering _start_workers...", logging.DEBUG)
        if self.started:
            self.log("Already started, returning.", logging.DEBUG)
            return
        self.started = True

        self.loop = asyncio.get_running_loop()
        self.loop.set_default_executor(
            ThreadPoolExecutor(max_workers=self.thread_pool_size)
        )
        self._completion_queue = asyncio.Queue()
        self._shutdown_event = asyncio.Event()
        self._worker_crash_event = asyncio.Event()

        for worker in self.workers:
            worker.start()
            if worker._process.pid:
                self._pid_to_worker_map[worker._process.pid] = worker
            self.log(
                message=f"Started worker with id {worker.identity.id} and name {worker.identity.name}",
                level=logging.DEBUG,
            )
        self.log("All worker processes starting.", logging.DEBUG)

        # Set up a signal handler for child process termination to detect crashes.
        self.loop.add_signal_handler(signal.SIGCHLD, self._handle_sigchld)

        # Result collector only needs to wait for EOQ from task workers, which are
        # shut down first.
        num_task_workers = len(
            [
                w
                for w in self.workers
                if w.ipc.queues
                and "result" in w.ipc.queues
                and w.identity.name
                and "log-worker" not in w.identity.name
            ]
        )
        self._result_collection_task = self.loop.create_task(
            self._collect_results_continuously_async(
                num_workers_to_expect=num_task_workers,
                completion_queue=self._completion_queue,
            )
        )
        self.log("Result collector task started.", logging.DEBUG)

        self._requeue_listener_task = self.loop.create_task(
            self._requeue_listener_async()
        )
        self.log("Requeue listener task started.", logging.DEBUG)

        if self.show_progress:
            self.progress_thread = Thread(
                target=run_progress,
                args=(num_task_workers, self.progress_ipc),
                kwargs={"capture_dict": self.progress_state_capture_dict},
                daemon=True,
            )
            self.progress_thread.start()

    async def finish_tasks(self):
        """
        Asynchronously waits for all submitted tasks to complete by monitoring
        the central accounting system.
        """
        self.log("Entering finish_tasks...", logging.DEBUG)

        accounting_prop = self.props.get("accounting_store")
        accounting_store = accounting_prop.initializer if accounting_prop else None
        if accounting_store is None:
            self.log(
                "Accounting store not found, cannot use finish_tasks.", logging.WARNING
            )
            return

        if not self.workers:
            return

        while True:
            with accounting_store.lock:
                data = accounting_store._read_data()
                total_counts = data.get("Total", {})

                submitted = total_counts.get("initial", 0) + total_counts.get(
                    "generated", 0
                )
                completed = total_counts.get("completed", 0)
                failures = total_counts.get("failures", 0)
                skipped = total_counts.get("skipped", 0)
                cancelled = total_counts.get("cancelled", 0)
                expired = total_counts.get("expired", 0)
                finished = completed + failures + skipped + cancelled + expired

            requeue_is_empty = self.queues["requeue"].empty()

            # The loop exits when the requeue is empty AND the accounting
            # system confirms all work is finished.
            if requeue_is_empty and finished >= submitted:
                # To handle the race condition where a producer task increments 'completed'
                # before its generated task increments 'generated', we give a moment for
                # the system to stabilize and then re-check the final counts.
                await asyncio.sleep(0.05)
                with accounting_store.lock:
                    data = accounting_store._read_data()
                    total_counts = data.get("Total", {})
                    final_submitted = total_counts.get(
                        "initial", 0
                    ) + total_counts.get("generated", 0)

                if finished >= final_submitted:
                    self.log(
                        f"All {finished} of {final_submitted} tasks have finished.",
                        logging.INFO,
                    )
                    break

            # Wait for either the next task to complete (the signal) or a worker to crash.
            completion_waiter = self.loop.create_task(self._completion_queue.get())
            crash_waiter = self.loop.create_task(self._worker_crash_event.wait())

            done, pending = await asyncio.wait(
                [completion_waiter, crash_waiter],
                return_when=asyncio.FIRST_COMPLETED,
            )

            if crash_waiter in done:
                completion_waiter.cancel()
                crashed_worker_name = "unknown"
                for worker in self.workers:
                    if not worker._process.is_alive():
                        crashed_worker_name = worker.identity.name
                        break
                error_msg = f"Worker {crashed_worker_name} crashed. Aborting wait."
                self.log(error_msg, logging.CRITICAL)
                raise WorkerCrashError(error_msg)

            if completion_waiter in done:
                crash_waiter.cancel()
                self._completion_queue.task_done()

            await asyncio.sleep(0)

    def _get_buffered_results(self) -> list[Task]:
        """Returns and clears the internal results buffer in a thread-safe manner."""
        with self._results_buffer_lock:
            results = self._results_buffer
            self._results_buffer = []
            return results

    def get_results(self) -> Generator[Task]:
        """
        Yields all results collected from workers that are currently in the buffer.
        This method is non-blocking and provides a snapshot of completed tasks.
        """
        self.log(message="Getting results from buffer", level=logging.INFO)

        # Yield all results currently held in the thread-safe buffer.
        # The background result collector thread is the only component that
        # interacts with the multiprocessing result queue.
        buffered = self._get_buffered_results()
        for item in buffered:
            # Hide internal tasks from the user based on the system hooks.
            suppress = False
            if "should_suppress_result" in self.orchestrator_system_registry:
                for system_func in self.orchestrator_system_registry[
                    "should_suppress_result"
                ]:
                    if system_func(item):
                        suppress = True
                        break
            if suppress:
                continue
            yield item

    async def _final_requeue_drain(self) -> list[Task]:
        """
        Performs a one-time drain of the central requeue queue during shutdown.
        Returns the list of tasks that were drained and re-queued.
        """
        self.log("Performing final drain of requeue queue.", logging.DEBUG)
        tasks_from_q = await self.loop.run_in_executor(
            None,
            partial(drain_queue_non_blocking, trait_registry=self.trait_registry),
            self.queues["requeue"],
        )
        found_tasks = tasks_from_q or []

        if found_tasks:
            self.log(
                f"Final drain found {len(found_tasks)} tasks to redistribute.",
                logging.DEBUG,
            )
            await self.add_tasks(found_tasks, _from_poller=True)

        return found_tasks

    async def _shutdown(self) -> None:
        """Gracefully stops all workers and cleans up all resources."""
        self.log("Entering _shutdown...", logging.DEBUG)
        if not self.started:
            self.log(
                message="Orchestrator not started. No workers to stop.",
                level=logging.INFO,
            )
            return

        if self.stopped:
            self.log(
                message="Orchestrator already stopped. Ignoring call.",
                level=logging.WARNING,
            )
            return
        self.stopped = True

        # Remove the signal handler to prevent race conditions during graceful shutdown.
        if self.loop and self.started:
            try:
                self.loop.remove_signal_handler(signal.SIGCHLD)
            except RuntimeError:
                # Can happen if the event loop is already closed, safe to ignore.
                pass

        self.log(
            message="Shutting down workers and cleaning up resources.",
            level=logging.INFO,
        )

        # Partition workers to maintain shutdown order (task workers first, then log workers)
        log_workers = [
            w
            for w in self.workers
            if w.identity.name and "log-worker" in w.identity.name
        ]
        task_workers = [
            w
            for w in self.workers
            if not w.identity.name or "log-worker" not in w.identity.name
        ]

        # 1. Signal task workers to exit gracefully.
        self.log("Signaling task workers to exit.", logging.INFO)
        for worker in task_workers:
            next(iter(worker.ipc.control_queues.values())).put(Task(action="exit"))
        self.log("Sent exit signal to all task workers.", logging.DEBUG)

        # 2. Wait for task worker processes to terminate. This is safer than joining queues,
        # as it won't hang if a worker has already crashed.
        self.log("Joining task worker processes", logging.INFO)

        self.log("Waiting to join task worker processes...", logging.DEBUG)
        await asyncio.gather(
            *(self._join_or_terminate_process(w) for w in task_workers)
        )
        self.log("Task worker processes joined.", logging.DEBUG)
        self.log(message="All task workers have exited", level=logging.INFO)

        # Now that task workers are stopped, perform a final drain of the requeue queues
        # to catch any last-minute logs they may have sent.
        drained_tasks = await self._final_requeue_drain()
        if drained_tasks:
            self.log(
                f"Waiting for {len(drained_tasks)} final log messages to be processed.",
                logging.DEBUG,
            )
            for _ in range(len(drained_tasks)):
                await self._completion_queue.get()
                self._completion_queue.task_done()
            self.log("Final log messages processed.", logging.DEBUG)

        # Before signaling the final shutdown, wait for log workers to be idle.
        # This ensures all log messages generated during shutdown are processed.
        await self._wait_for_log_workers_to_idle()

        self.log("Stop event set for background tasks.", logging.DEBUG)
        if self._shutdown_event:
            self._shutdown_event.set()

        if self._requeue_listener_task and not self._requeue_listener_task.done():
            try:
                await self._requeue_listener_task
            except asyncio.CancelledError:
                pass  # This is not expected now, but safe to keep.
            self.log("Requeue listener task finished.", logging.DEBUG)

        # Now that processes are stopped, we can safely close the control queues.
        for worker in task_workers:
            for cq in worker.ipc.control_queues.values():
                cq.close()
        self.log("Worker control queues closed.", logging.DEBUG)

        # 3. Now that workers are terminated, clean up queues without joining.
        # Joining a queue after its consumer process may have been killed can
        # lead to a permanent deadlock if the killed process did not call
        # task_done() for an item it retrieved.
        self.log("Cleaning up worker queues.", logging.DEBUG)

        if self._result_collection_task:
            await self._result_collection_task
            self.log("Result collector task finished.", logging.DEBUG)

        # Drain any remaining results from the buffer so they are not lost,
        # though standard usage should retrieve results before shutdown.
        self._get_buffered_results()

        if self.show_progress and self.progress_ipc and self.progress_thread:
            self.progress_ipc["stop_event"].set()
            # Also set the update_event to wake the progress thread immediately.
            if "update_event" in self.progress_ipc:
                self.progress_ipc["update_event"].set()
            await asyncio.to_thread(self.progress_thread.join)

        # Signal the logger to exit.
        self.log("Signaling loggers to exit.", logging.DEBUG)
        for worker in log_workers:
            next(iter(worker.ipc.control_queues.values())).put(Task(action="exit"))

        self.log("Waiting to join logger processes...", logging.DEBUG)
        await asyncio.gather(*(self._join_or_terminate_process(w) for w in log_workers))
        self.log("Logger processes joined.", logging.DEBUG)

        # Now that log workers have stopped, we can safely close their control queues.
        for worker in log_workers:
            # Do not join the control queue, as it creates a race condition.
            # We have already joined the process itself, which is a more reliable signal.
            for cq in worker.ipc.control_queues.values():
                cq.close()
        self.log("Logger control queues closed.", logging.DEBUG)

        # Final cleanup of all shared memory queues and buffers
        for q in self.queues.values():
            q.close()
            try:
                q.unlink()
            except FileNotFoundError:
                # Can happen if already unlinked, safe to ignore.
                pass
        for buffer in self.batch_buffers:
            buffer.close_and_unlink()

        # Final cleanup for auto-provisioned resources
        self.log("Cleaning up auto-provisioned resources.", logging.DEBUG)
        for resource in self._resources_to_cleanup:
            if hasattr(resource, "close"):
                resource.close()
            if hasattr(resource, "unlink"):
                try:
                    resource.unlink()
                except FileNotFoundError:
                    pass

    async def _send_one_sub_batch(self, buffer: Buffer, sub_batch: list[Task]) -> int:
        """Sends a single sub-batch that is known to fit in the buffer."""
        packed_batch = msgpack.packb(
            [t.model_dump(mode="python") for t in sub_batch],
            default=default_encoder,
            use_bin_type=True,
        )

        # Asynchronously wait for the worker to signal it's ready, without blocking a thread.
        future = self.loop.create_future()
        pipe_fd = buffer.producer_ready_rx.fileno()

        def wakeup_callback():
            if not future.done():
                future.set_result(True)

        self.loop.add_reader(pipe_fd, wakeup_callback)

        try:
            # Wait for the worker to signal it's ready for this batch.
            await future
            # Drain the pipe to clear the signal.
            while buffer.producer_ready_rx.poll():
                buffer.producer_ready_rx.recv_bytes()
        finally:
            self.loop.remove_reader(pipe_fd)

        # Now that we've been signaled, acquire the semaphore. This should not block,
        # but we still use an executor as it's a sync call.
        await self.loop.run_in_executor(None, buffer.producer_semaphore.acquire)
        try:
            with buffer.lock:
                buffer.buf[_HEADER.size : _HEADER.size + len(packed_batch)] = (
                    packed_batch
                )
                buffer.data_length.value = len(packed_batch)
                buffer.state.value = BufferState.READY_FOR_WORKER.value
            buffer.wakeup_tx.send_bytes(b"\0")
            return len(sub_batch)
        except Exception:
            # If something goes wrong after acquiring the semaphore, we must release it.
            buffer.producer_semaphore.release()
            raise

    async def _send_batches_to_worker(
        self, buffer: Buffer, batch: list[Task], enqueue_failures: list[Task]
    ) -> int:
        """Splits a large batch into buffer-sized sub-batches and sends them sequentially."""
        successfully_added_count = 0
        sub_batch: list[Task] = []
        for task in batch:
            try:
                packed_single = msgpack.packb(
                    [task.model_dump(mode="python")],
                    default=default_encoder,
                    use_bin_type=True,
                )
                if len(packed_single) > buffer.spec.size:
                    enqueue_failures.append(task)
                    continue
            except (ValueError, TypeError, AttributeError):
                enqueue_failures.append(task)
                continue

            packed_potential = msgpack.packb(
                [t.model_dump(mode="python") for t in sub_batch + [task]],
                default=default_encoder,
                use_bin_type=True,
            )

            if len(packed_potential) > buffer.spec.size and sub_batch:
                successfully_added_count += await self._send_one_sub_batch(
                    buffer, sub_batch
                )
                sub_batch = [task]
            else:
                sub_batch.append(task)

        if sub_batch:
            successfully_added_count += await self._send_one_sub_batch(
                buffer, sub_batch
            )
        return successfully_added_count

    async def add_task(self, task: Task):
        """Adds a single task to the queue. Convenience wrapper around add_tasks."""
        await self.add_tasks([task])

    async def add_tasks(
        self,
        tasks: list[Task],
        _from_poller: bool = False,
    ) -> list[Task]:
        """Adds a batch of tasks to the workers using shared memory buffers."""
        consumers_to_wait = []
        tasks_to_run_now = []
        if not _from_poller:
            for task in tasks:
                if any(isinstance(t, ConsumesTrait) for t in task.traits):
                    consumers_to_wait.append(task)
                else:
                    tasks_to_run_now.append(task)
        else:
            tasks_to_run_now = tasks

        if consumers_to_wait:
            affected_tags = set()
            for consumer in consumers_to_wait:
                consumes_trait = next(
                    t for t in consumer.traits if isinstance(t, ConsumesTrait)
                )
                # The primary tag is the first one in the list. This is the
                # key for grouping consumers and their results.
                primary_tag = consumes_trait.tags[0]
                self._waiting_consumers[primary_tag].append(consumer)
                affected_tags.add(primary_tag)

            if affected_tags:
                await self._check_and_emit_consumers(affected_tags)

        if not _from_poller:
            self.log(
                f"Entering add_tasks for {len(tasks_to_run_now)} tasks...",
                logging.DEBUG,
            )
        # The task_store has been removed. Task completion is now tracked solely
        # by the accounting system.

        if not self.started:
            await self.start_workers()

        if not self.workers:
            return tasks_to_run_now

        if not tasks_to_run_now:
            return []

        enqueue_failures: list[Task] = []

        # Partition tasks based on worker affinity by consulting traits.
        specific_worker_tasks: dict[str, list[Task]] = {}
        any_worker_tasks = []
        task_workers = [
            w
            for w in self.workers
            if not w.identity.name or "log-worker" not in w.identity.name
        ]

        for task in tasks_to_run_now:
            eligible_workers = self.workers
            # Allow each trait to progressively filter the list of eligible workers.
            if "on_task_routed" in self.orchestrator_system_registry:
                for system_func in self.orchestrator_system_registry["on_task_routed"]:
                    new_eligible = system_func(task, eligible_workers)
                    # A system hook returns a new list of workers. If it returns None,
                    # it means it didn't apply to this task, so we keep the existing list.
                    if new_eligible is not None:
                        eligible_workers = new_eligible

            if len(eligible_workers) == 1:
                # The task is pinned to a single worker.
                worker_name = eligible_workers[0].identity.name
                specific_worker_tasks.setdefault(worker_name, []).append(task)
            elif len(eligible_workers) == 0:
                self.log(
                    f"No eligible workers found for task {task.id} after trait filtering. Task will not be executed.",
                    logging.WARNING,
                )
                enqueue_failures.append(task)
            else:
                # Multiple workers are eligible; add to the round-robin pool.
                any_worker_tasks.append(task)

        worker_map = {w.identity.name: w for w in self.workers}

        send_coroutines = []

        # 1. Distribute tasks for any worker (round-robin to task workers)
        if any_worker_tasks and task_workers:
            worker_batches: list[list[Task]] = [[] for _ in task_workers]
            for i, task in enumerate(any_worker_tasks):
                worker_batches[i % len(task_workers)].append(task)

            for i, batch in enumerate(worker_batches):
                if batch:
                    send_coroutines.append(
                        self._send_batches_to_worker(
                            task_workers[i].ipc.batch_buffer, batch, enqueue_failures
                        )
                    )

        # 2. Distribute tasks for specific workers
        for worker_name, batch in specific_worker_tasks.items():
            if worker_name in worker_map:
                worker = worker_map[worker_name]
                send_coroutines.append(
                    self._send_batches_to_worker(
                        worker.ipc.batch_buffer, batch, enqueue_failures
                    )
                )
            else:
                self.log(
                    f"Worker '{worker_name}' not found for {len(batch)} tasks. These tasks will not be executed.",
                    logging.WARNING,
                )
                enqueue_failures.extend(batch)

        results = await asyncio.gather(*send_coroutines)
        successfully_added_count = sum(results)

        # Task submission no longer directly mutates any orchestrator counters.
        # All counting is now handled by the accounting system within the workers.
        if not _from_poller:
            self.log(
                message=f"Added {successfully_added_count} tasks. Failures: {len(enqueue_failures)}",
                level=logging.DEBUG,
            )
        return enqueue_failures
