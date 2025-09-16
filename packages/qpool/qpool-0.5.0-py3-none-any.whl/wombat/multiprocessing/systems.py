from __future__ import annotations

import asyncio
import hashlib
import inspect
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    List,
    Type,
)

import msgpack

from wombat.multiprocessing.errors import EvaluationFailureError
from wombat.multiprocessing.ipc.utilities import AsyncProcessLock, default_encoder
from wombat.multiprocessing.traits.accounting import (
    AccountingTrait,
    GeneratedTrait,
    UncountedTrait,
)
from wombat.multiprocessing.traits.breaker import BreakerTrait, CircuitBreakerState
from wombat.multiprocessing.traits.consumes import ConsumesTrait
from wombat.multiprocessing.traits.debounce import DebounceTrait
from wombat.multiprocessing.traits.delayed import DelayedTrait
from wombat.multiprocessing.traits.evaluatable import EvaluatableTrait
from wombat.multiprocessing.traits.expirable import ExpirableTrait
from wombat.multiprocessing.traits.lifecycle import (
    Attempting,
    Cancelled,
    Created,
    Expired,
    Failed,
    LifecycleManagerTrait,
    QueuedTrait,
    RetryingTrait,
    Skipped,
    Succeeded,
)
from wombat.multiprocessing.traits.loggable import LoggableTrait, LogCarrierTrait
from wombat.multiprocessing.traits.pinned import PinnedTrait
from wombat.multiprocessing.traits.produces import ProducesTrait
from wombat.multiprocessing.traits.rate_limit import RateLimitTrait
from wombat.multiprocessing.traits.requires_props import RequiresPropsTrait
from wombat.multiprocessing.traits.retryable import RetryableTrait
from wombat.multiprocessing.traits.tagged import TaggedTrait
from wombat.multiprocessing.traits.timeout import TimeoutTrait
from wombat.multiprocessing.traits.models import Task


def priority(level: int):
    """A decorator to assign a priority level to a system hook."""

    def wrapper(func):
        setattr(func, "_hook_priority", level)
        return func

    return wrapper


if TYPE_CHECKING:
    from wombat.multiprocessing.orchestrator import Orchestrator, OrchestratorBuilder
    from wombat.multiprocessing.traits.models import BaseTrait
    from wombat.multiprocessing.worker import Worker


class BaseSystem:
    """Base class for all systems."""

    # A system declares the data components it operates on.
    required_traits: ClassVar[List[Type[BaseTrait]]] = []


async def _increment_raw_count(worker: "Worker", key: str, value: int = 1):
    """A raw, non-idempotent counter increment for accounting."""
    accounting_store = worker.props["accounting_store"].instance
    worker_key = worker.identity.name
    async_lock = AsyncProcessLock(accounting_store.lock, worker.runtime_state.loop)

    async with async_lock:
        data = accounting_store._read_data()

        worker_counts = data.get(worker_key, {})
        worker_counts[key] = worker_counts.get(key, 0) + value
        data[worker_key] = worker_counts

        total_counts = data.get("Total", {})
        total_counts[key] = total_counts.get(key, 0) + value
        data["Total"] = total_counts

        accounting_store._write_data(data)


class AccountingSystem(BaseSystem):
    """System that handles the accounting logic for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [
        AccountingTrait,
        UncountedTrait,
        GeneratedTrait,
        Cancelled,
        Skipped,
        Expired,
    ]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions a `SharedMemoryDict` for accounting if not already present.

        This build hook ensures that the necessary shared memory resource for
        storing task counts is created and managed by the orchestrator.
        """
        if "accounting_store" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            # Give it a decent size to avoid overflow with many workers/counters
            shm_dict = SharedMemoryDict.create(
                context=context, max_size=1024 * 1024, purpose="accounting"
            )
            builder.register_resource_for_cleanup(shm_dict)
            builder.props["accounting_store"] = Prop(
                initializer=shm_dict,
                use_context_manager=False,
            )

    @staticmethod
    async def _increment_count(
        worker: "Worker", accounting_trait: "AccountingTrait", key: str, value: int = 1
    ):
        # Retries are cumulative and not idempotent, so they bypass the `counted` check.
        if key != "retries":
            if accounting_trait.counted.get(key):
                return

        await _increment_raw_count(worker, key, value)

        if key != "retries":
            accounting_trait.counted[key] = True

    @staticmethod
    @priority(500)
    async def on_task_received(task: "Task", worker: "Worker") -> None:
        """
        Processes 'received' counting rules from other traits.

        This hook is responsible for the 'initial' and 'generated' counts. After
        counting, it removes the `Uncounted` or `Generated` marker traits to
        prevent re-counting on retries.
        """
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return

        processed_a_received_event = False
        # Iterate over a copy, as we may modify the list.
        for trait in task.traits[:]:
            if trait.counting_rules:
                for rule in trait.counting_rules:
                    if rule.on_event == "received":
                        await AccountingSystem._increment_count(
                            worker, accounting_trait, rule.counter_name
                        )
                        processed_a_received_event = True

        if processed_a_received_event:
            task.remove_traits_by_type(UncountedTrait, GeneratedTrait)

    @staticmethod
    @priority(850)
    async def on_task_cancelled(task: "Task", worker: "Worker"):
        """On cancellation, increment the cancelled counter."""
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return

        await AccountingSystem._increment_count(worker, accounting_trait, "cancelled")

    @staticmethod
    @priority(850)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """On success, increment the completed counter and process 'success' rules."""
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return None

        await AccountingSystem._increment_count(worker, accounting_trait, "completed")
        for trait in task.traits:
            if trait.counting_rules:
                for rule in trait.counting_rules:
                    if rule.on_event == "success":
                        await AccountingSystem._increment_count(
                            worker, accounting_trait, rule.counter_name
                        )
        return None

    @staticmethod
    @priority(850)
    async def on_task_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """On failure, increment the appropriate counter (failure or retry)."""
        accounting_trait = next(
            (t for t in task.traits if isinstance(t, AccountingTrait)), None
        )
        if not accounting_trait:
            return

        is_retry = any(isinstance(t, RetryingTrait) for t in task.traits)
        base_event = "retries" if is_retry else "failures"
        rule_event = "retry" if is_retry else "failure"

        await AccountingSystem._increment_count(worker, accounting_trait, base_event)

        for trait in task.traits:
            if trait.counting_rules:
                for rule in trait.counting_rules:
                    if rule.on_event == rule_event:
                        await AccountingSystem._increment_count(
                            worker, accounting_trait, rule.counter_name
                        )


class BreakerSystem(BaseSystem):
    """System that implements the Circuit Breaker pattern."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [BreakerTrait, Failed]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions the necessary lock and shared dictionary for circuit breakers.

        This build hook ensures that the `breaker_lock` and `breaker_states`
        props are available for all workers if any task uses the `Breaker` trait.
        """
        from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict
        from wombat.multiprocessing.traits.models import Prop

        context = builder.context

        if "breaker_lock" not in builder.props:
            lock = context.Lock()
            builder.props["breaker_lock"] = Prop(
                initializer=lock, use_context_manager=False
            )

        if "breaker_states" not in builder.props:
            shm_dict = SharedMemoryDict.create(context=context, purpose="breaker")
            builder.register_resource_for_cleanup(shm_dict)
            builder.props["breaker_states"] = Prop(
                initializer=shm_dict,
                use_context_manager=False,
            )

    @staticmethod
    def _get_circuit_key(task: "Task", breaker_trait: "BreakerTrait") -> str:
        """The key is based on the group, as the circuit protects a shared resource."""
        return breaker_trait.group or task.action

    @staticmethod
    @priority(100)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """
        Checks the state of the circuit before executing the task.

        If the circuit is OPEN, it prevents execution. If it has been OPEN for
        longer than the `recovery_timeout`, it transitions to HALF_OPEN to allow
        a single task to test the downstream service.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return True, task

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)
        now = worker.get_time()

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                # Lazily initialize the state for this circuit.
                shared_state = {
                    "state": CircuitBreakerState.CLOSED.value,
                    "failures": 0,
                    "opened_at": 0.0,
                }
                states_dict[key] = shared_state
                return True, task

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.OPEN:
                if now - shared_state["opened_at"] > breaker_trait.recovery_timeout:
                    shared_state["state"] = CircuitBreakerState.HALF_OPEN.value
                    states_dict[key] = shared_state
                    worker.log(
                        f"Circuit breaker for {key} is now HALF_OPEN.", logging.INFO
                    )
                    return True, task  # Allow one test task
                else:
                    task.replace_trait(Failed())
                    return False, task  # Block execution
            return True, task
        finally:
            lock.release()

    @staticmethod
    @priority(300)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        Resets the circuit breaker to CLOSED on a successful execution.

        If the circuit was in the HALF_OPEN state, a successful task execution
        is taken as a sign that the downstream service has recovered, so the
        circuit is closed and the failure count is reset. A successful task also
        resets the failure count if the circuit is currently CLOSED.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return None

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                return None

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.HALF_OPEN:
                worker.log(f"Circuit breaker for {key} has CLOSED.", logging.INFO)
                shared_state["state"] = CircuitBreakerState.CLOSED.value
                shared_state["failures"] = 0
                states_dict[key] = shared_state
            elif (
                current_state == CircuitBreakerState.CLOSED
                and shared_state["failures"] > 0
            ):
                worker.log(
                    f"Resetting failure count for {key} after success.", logging.DEBUG
                )
                shared_state["failures"] = 0
                states_dict[key] = shared_state
        finally:
            lock.release()
        return None

    @staticmethod
    @priority(200)
    async def on_task_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """
        Increments the failure count and potentially opens the circuit.

        If a task fails while the circuit is CLOSED, the failure count is
        incremented. If the count exceeds the `failure_threshold`, the circuit
        transitions to the OPEN state. If a task fails while HALF_OPEN, the
        circuit transitions back to OPEN.
        """
        breaker_trait = next((t for t in task.traits if isinstance(t, BreakerTrait)), None)
        if not breaker_trait:
            return

        lock = worker.props["breaker_lock"].instance
        states_dict = worker.props["breaker_states"].instance
        key = BreakerSystem._get_circuit_key(task, breaker_trait)
        now = worker.get_time()

        await worker.runtime_state.loop.run_in_executor(None, lock.acquire)
        try:
            shared_state = states_dict.get(key)
            if not shared_state:
                return

            current_state = CircuitBreakerState(shared_state["state"])
            if current_state == CircuitBreakerState.HALF_OPEN:
                shared_state["state"] = CircuitBreakerState.OPEN.value
                shared_state["opened_at"] = now
                worker.log(
                    f"Circuit for {key} failed in HALF_OPEN, re-opening.",
                    logging.WARNING,
                )
            elif current_state == CircuitBreakerState.OPEN:
                # The circuit is already open, do nothing.
                pass
            elif current_state == CircuitBreakerState.CLOSED:
                shared_state["failures"] += 1
                if shared_state["failures"] >= breaker_trait.failure_threshold:
                    shared_state["state"] = CircuitBreakerState.OPEN.value
                    shared_state["opened_at"] = now
                    worker.log(
                        f"Circuit for {key} has OPENED due to {shared_state['failures']} failures.",
                        logging.WARNING,
                    )
            states_dict[key] = shared_state
        finally:
            lock.release()


class DebounceSystem(BaseSystem):
    """System to prevent duplicate task execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [DebounceTrait, Skipped]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        """
        Auto-provisions a `SharedMemoryDict` for deduplication if not already present.

        This build hook ensures that the necessary shared memory resource for
        storing task execution timestamps is created and managed by the
        orchestrator.
        """
        if "deduplication_cache" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            shm_dict = SharedMemoryDict.create(context=context, purpose="debounce")
            builder.register_resource_for_cleanup(shm_dict)
            builder.props["deduplication_cache"] = Prop(
                initializer=shm_dict,
                use_context_manager=False,
            )

    @staticmethod
    def _get_task_key(task: "Task", debounce_trait: "DebounceTrait") -> str:
        """
        Creates a stable, unique key for deduplication.

        If a `group` is provided, all tasks in that group are considered
        duplicates of each other, regardless of their action or arguments. The
        key will be the group name itself.

        If no `group` is provided, the key is generated from the task's action
        name and a hash of its arguments, ensuring only identical tasks are
        deduplicated.
        """
        if debounce_trait.group:
            return debounce_trait.group

        # Create a stable representation of the task's arguments.
        args_bytes = msgpack.packb(
            (task.args, task.kwargs), default=default_encoder, use_bin_type=True
        )
        # Use a stable hash algorithm to ensure the key is consistent across processes.
        hasher = hashlib.sha256()
        hasher.update(args_bytes)
        return f"{task.action}:{hasher.hexdigest()}"

    @staticmethod
    @priority(110)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """
        Checks if a similar task has run recently and skips execution if so.

        This hook calculates a unique key for the task based on its action and
        arguments. It then checks a shared cache to see if a task with the
        same key has executed within the configured `window`. If it has, the
        task is marked as `skipped`. Otherwise, the current time is recorded
        and execution proceeds.
        """
        debounce_trait = next((t for t in task.traits if isinstance(t, DebounceTrait)), None)
        if not debounce_trait:
            return True, task

        key = DebounceSystem._get_task_key(task, debounce_trait)
        now = worker.get_time()

        dedupe_cache = worker.props["deduplication_cache"].instance
        async_lock = AsyncProcessLock(dedupe_cache.lock, worker.runtime_state.loop)

        async with async_lock:
            data = dedupe_cache._read_data()
            last_seen = data.get(key)

            if last_seen and (
                now - last_seen <= debounce_trait.window.total_seconds()
            ):
                worker.log(
                    f"Task {task.id} (key: {key}) is a duplicate within the {debounce_trait.window} window. Skipping.",
                    logging.INFO,
                )
                task.replace_trait(Skipped())
                return False, task

            data[key] = now
            dedupe_cache._write_data(data)
            return True, task


class DelayedSystem(BaseSystem):
    """System to delay task execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [DelayedTrait]

    @staticmethod
    @priority(140)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """Waits for the specified delay before proceeding with execution."""
        delayed_trait = next((t for t in task.traits if isinstance(t, DelayedTrait)), None)
        if not delayed_trait:
            return True, task

        await asyncio.sleep(delayed_trait.delay)
        return True, task


class EvaluatableSystem(BaseSystem):
    """System for post-execution result evaluation."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [EvaluatableTrait]

    @staticmethod
    async def _evaluate(evaluatable_trait: "EvaluatableTrait", data: Any) -> bool:
        """
        Runs the provided evaluator function against the task result.

        This method supports both synchronous and asynchronous evaluator functions.

        Args:
            data: The result of the task's action.

        Returns:
            `True` if the evaluation passes or if no evaluator is configured,
            `False` otherwise.
        """
        if not evaluatable_trait.evaluator:
            return True

        evaluation = evaluatable_trait.evaluator(data)
        if inspect.isawaitable(evaluation):
            return await evaluation
        return evaluation

    @staticmethod
    @priority(100)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        On success, evaluates the result. If the evaluation fails, it raises
        an `EvaluationFailureError` to trigger the standard failure-handling
        path in the worker.
        """
        evaluatable_trait = next(
            (t for t in task.traits if isinstance(t, EvaluatableTrait)), None
        )
        if not evaluatable_trait:
            return None

        if not await EvaluatableSystem._evaluate(evaluatable_trait, result):
            # Raise an exception to trigger the on_task_failure lifecycle.
            raise EvaluationFailureError(f"Evaluation failed for result: {result!r}")

        # If the evaluation is successful, do nothing.
        return None


class ExpirableSystem(BaseSystem):
    """System to handle task expiration."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ExpirableTrait, Expired]

    @staticmethod
    def _is_expired(expirable_trait: "ExpirableTrait") -> bool:
        if not expirable_trait.expires_at:
            return False
        # utc_datetime is defined in wombat.multiprocessing.traits.models
        from wombat.multiprocessing.traits.models import utc_datetime

        return utc_datetime() >= expirable_trait.expires_at

    @staticmethod
    @priority(120)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """Hook to check for expiration before execution."""
        expirable_trait = next(
            (t for t in task.traits if isinstance(t, ExpirableTrait)), None
        )
        if not expirable_trait:
            return True, task

        if ExpirableSystem._is_expired(expirable_trait):
            worker.log(
                f"Task {getattr(task, 'id', 'N/A')} expired and was skipped.",
                logging.INFO,
            )
            task.replace_trait(Expired())
            return False, task  # Prevent execution
        return True, task


class LifecycleSystem(BaseSystem):
    """System that manages the lifecycle state of a task."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [
        LifecycleManagerTrait,
        QueuedTrait,
        RetryingTrait,
        Created,
        Attempting,
        Succeeded,
        Cancelled,
        Failed,
    ]

    # --- From LifecycleManager ---
    @staticmethod
    @priority(100)
    async def on_task_attempt(task: "Task", worker: "Worker") -> "Task":
        """Sets the task's state to Attempting."""
        if not any(isinstance(t, LifecycleManagerTrait) for t in task.traits):
            return task
        task.remove_traits_by_type(RetryingTrait, QueuedTrait, Created)
        task.replace_trait(Attempting())
        return task

    @staticmethod
    @priority(800)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """Sets the task's state to Succeeded."""
        if not any(isinstance(t, LifecycleManagerTrait) for t in task.traits):
            return None
        task.remove_traits_by_type(Attempting)
        task.replace_trait(Succeeded())
        return None

    @staticmethod
    @priority(800)
    async def on_task_cancelled(task: "Task", worker: "Worker"):
        """Sets the task's state to Cancelled."""
        if not any(isinstance(t, LifecycleManagerTrait) for t in task.traits):
            return
        task.remove_traits_by_type(Attempting)
        task.replace_trait(Cancelled())

    @staticmethod
    @priority(900)
    async def on_task_terminal_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """Sets the task's state to Failed."""
        if not any(isinstance(t, LifecycleManagerTrait) for t in task.traits):
            return
        task.remove_traits_by_type(Attempting)
        task.replace_trait(Failed())

    # --- From Queued ---
    @staticmethod
    @priority(500)
    def on_task_submitted(task: "Task", is_resubmission: bool) -> bool | None:
        """
        Determines if a task should be counted for completion tracking.

        By default, tasks are counted. Retrying tasks are not, as they are not
        new submissions.
        """
        # A queued task is always a new task.
        if any(isinstance(t, QueuedTrait) for t in task.traits):
            return True
        # A retrying task is not a new submission and should not be counted.
        if any(isinstance(t, RetryingTrait) for t in task.traits):
            return False
        # The default behavior from BaseTrait is to count tasks, unless another
        # system hook (like for Retryable) has returned False.
        return True

    # --- From Retrying ---
    @staticmethod
    @priority(500)
    async def on_task_requeued(task: "Task", orchestrator: "Orchestrator") -> bool:
        """Handle requeueing for a retry task."""
        if not any(isinstance(t, RetryingTrait) for t in task.traits):
            return False
        await orchestrator.add_tasks([task], _from_poller=True)
        return True

    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """Suppresses the result for a retry attempt from being yielded."""
        return any(isinstance(t, RetryingTrait) for t in task.traits)


class LoggableSystem(BaseSystem):
    """System to handle logging for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [LoggableTrait, LogCarrierTrait]

    # --- From Loggable ---
    @staticmethod
    @priority(800)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        """Hook executed before the task's action is run."""
        if any(isinstance(t, LoggableTrait) for t in task.traits):
            worker.log(f"Executing task {task.id} ({task.action})", logging.DEBUG)
        return True, task

    @staticmethod
    @priority(900)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """Hook executed after the task's action runs successfully."""
        loggable_trait = next((t for t in task.traits if isinstance(t, LoggableTrait)), None)
        if loggable_trait:
            worker.log(
                f"Task {task.id} ({task.action}) finished successfully.",
                loggable_trait.log_level,
            )
        return None

    @staticmethod
    @priority(900)
    async def on_task_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """Hook executed when the task's action raises an exception."""
        if any(isinstance(t, LoggableTrait) for t in task.traits):
            worker.log(
                f"Task {task.id} ({task.action}) failed with exception: {exception}",
                logging.ERROR,
            )

    # --- From LogCarrier ---
    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """Suppresses the result of this task from being yielded by the orchestrator."""
        return any(isinstance(t, LogCarrierTrait) for t in task.traits)

    @staticmethod
    @priority(500)
    def should_log_failure(task: "Task", worker: "Worker") -> bool:
        """Prevents logging a failure for this task to avoid logging cycles."""
        return not any(isinstance(t, LogCarrierTrait) for t in task.traits)


class PinnedSystem(BaseSystem):
    """System to handle task pinning."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [PinnedTrait]

    @staticmethod
    @priority(500)
    def on_task_routed(task: "Task", workers: list["Worker"]) -> list["Worker"] | None:
        """Filters the list of workers to only the one matching the pinned name."""
        pinned_trait = next((t for t in task.traits if isinstance(t, PinnedTrait)), None)
        if not pinned_trait:
            return None  # No change to routing
        return [w for w in workers if w.identity.name == pinned_trait.worker_name]


class ProducesSystem(BaseSystem):
    """System that allows a task to dynamically produce new tasks from its result."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ProducesTrait]

    @staticmethod
    def get_dependent_traits() -> list[Type[BaseTrait]]:
        """Declares that this system can add `GeneratedTrait`, `QueuedTrait`, and `TaggedTrait`."""
        return [GeneratedTrait, QueuedTrait, TaggedTrait]

    @staticmethod
    @priority(200)
    async def on_task_success(
        task: "Task", worker: "Worker", result: Any
    ) -> dict[str, Any] | None:
        """
        After the producer task succeeds, this hook checks if the result is one
        or more `Task` objects. If so, it requeues them for execution by the
        orchestrator.
        """
        produces_trait = next(
            (t for t in task.traits if isinstance(t, ProducesTrait)), None
        )
        if not produces_trait:
            return None

        tasks_to_requeue = []
        if isinstance(result, Task):
            tasks_to_requeue.append(result)
        elif isinstance(result, list) and all(isinstance(t, Task) for t in result):
            tasks_to_requeue.extend(result)

        if tasks_to_requeue:
            # Mark these tasks as generated and queued so they are counted correctly
            # and handled by the orchestrator's requeue listener.
            for new_task in tasks_to_requeue:
                new_task.add_trait(GeneratedTrait())
                new_task.add_trait(QueuedTrait())
                if produces_trait.tags:
                    new_task.add_trait(TaggedTrait(tags=produces_trait.tags))

            # Use asyncio.gather to requeue them concurrently.
            await asyncio.gather(
                *(
                    worker.requeue_task_locally(new_task)
                    for new_task in tasks_to_requeue
                )
            )

        return None

    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """
        Suppresses the result of the producer task from being yielded by the
        orchestrator, as its "result" is the creation of new tasks.
        """
        return any(isinstance(t, ProducesTrait) for t in task.traits)


class ConsumesSystem(BaseSystem):
    """System to handle the consumer side of a producer-consumer pattern."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [ConsumesTrait]

    @staticmethod
    @priority(500)
    def should_suppress_result(task: "Task") -> bool:
        """
        Suppresses the result of any tagged task, as its result is intended
        to be collected by a consumer, not yielded to the end user.
        """
        return any(isinstance(t, TaggedTrait) for t in task.traits)


class RateLimitSystem(BaseSystem):
    """System that limits the execution frequency of tasks within a group."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [RateLimitTrait]

    @staticmethod
    def before_build(builder: "OrchestratorBuilder", actions: dict[str, Callable]):
        if "rate_limit_cache" not in builder.props:
            from wombat.multiprocessing.ipc.shared_memory_dict import SharedMemoryDict
            from wombat.multiprocessing.traits.models import Prop

            context = builder.context
            shm_dict = SharedMemoryDict.create(context=context, purpose="rate_limit")
            builder.register_resource_for_cleanup(shm_dict)
            builder.props["rate_limit_cache"] = Prop(
                initializer=shm_dict,
                use_context_manager=False,
            )

    @staticmethod
    @priority(130)
    async def before_task_execution(
        task: "Task", worker: "Worker"
    ) -> tuple[bool, "Task"]:
        rate_limit_trait = next(
            (t for t in task.traits if isinstance(t, RateLimitTrait)), None
        )
        if not rate_limit_trait:
            return True, task

        rate_limit_cache = worker.props["rate_limit_cache"].instance
        async_lock = AsyncProcessLock(rate_limit_cache.lock, worker.runtime_state.loop)

        while True:
            now = worker.get_time()
            wait_time = 0

            await async_lock.acquire()
            try:
                all_timestamps = rate_limit_cache._read_data()
                group_timestamps = all_timestamps.get(rate_limit_trait.group, [])

                # Prune old timestamps
                period_seconds = rate_limit_trait.period.total_seconds()
                valid_timestamps = [
                    ts for ts in group_timestamps if now - ts < period_seconds
                ]

                if len(valid_timestamps) < rate_limit_trait.limit:
                    # We are within the limit, add our timestamp and proceed.
                    valid_timestamps.append(now)
                    all_timestamps[rate_limit_trait.group] = valid_timestamps
                    rate_limit_cache._write_data(all_timestamps)
                    return True, task  # Exit the loop and proceed with execution.

                # We are at the limit, calculate wait time.
                # Timestamps are sorted by insertion, so the first is the oldest.
                oldest_ts = valid_timestamps[0]
                wait_time = (oldest_ts + period_seconds) - now
            finally:
                await async_lock.release()

            if wait_time > 0:
                worker.log(
                    f"Rate limit for group '{rate_limit_trait.group}' reached. Waiting for {wait_time:.2f}s.",
                    logging.DEBUG,
                )
                await asyncio.sleep(wait_time)
            # After sleeping, loop again to re-evaluate.


class RequiresPropsSystem(BaseSystem):
    """System to inject props required by traits into task kwargs."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [RequiresPropsTrait]

    @staticmethod
    @priority(500)
    def before_prepare_arguments(
        task: "Task", worker: "Worker", kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Injects props into task kwargs based on trait requirements."""
        for trait in task.traits:
            props_to_add = {}
            if getattr(trait, "include_all_props", False):
                props_to_add = worker.props
            elif getattr(trait, "requires_props", None):
                props_to_add = {
                    k: v for k, v in worker.props.items() if k in trait.requires_props
                }

            if props_to_add:
                if "props" not in kwargs:
                    kwargs["props"] = {}
                # Do not overwrite existing props if they are already present.
                for key, value in props_to_add.items():
                    if key not in kwargs["props"]:
                        kwargs["props"][key] = value
        return kwargs


def linear_backoff(trait: "RetryableTrait") -> float:
    """Linear backoff function. Delay increases linearly with each retry."""
    return min(trait.max_delay, trait.initial_delay * trait.tries)


def exponential_backoff(trait: "RetryableTrait") -> float:
    """Exponential backoff function. Delay increases exponentially with each retry until max_delay is reached."""
    # The number of retries will be 1 for the first retry, 2 for the second, etc.
    # The exponent should be `retries - 1` to get a multiplier of 1x for the first retry.
    return min(
        trait.max_delay,
        trait.initial_delay * (trait.backoff_multiplier ** (trait.tries - 1)),
    )


class RetryableSystem(BaseSystem):
    """System that handles retry logic for tasks."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [
        RetryableTrait,
        RetryingTrait,
        Failed,
    ]

    @staticmethod
    def _backoff(retry_trait: "RetryableTrait") -> float:
        """Calculates the backoff delay for the next retry attempt."""
        if retry_trait.backoff_strategy == "linear":
            return linear_backoff(retry_trait)
        elif retry_trait.backoff_strategy == "custom" and retry_trait.backoff_function:
            return retry_trait.backoff_function(retry_trait)

        return exponential_backoff(retry_trait)

    @staticmethod
    @priority(100)
    async def on_task_failure(
        task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """Schedules a retry if the task has the RetryableTrait and tries remain."""
        retry_trait = next((t for t in task.traits if isinstance(t, RetryableTrait)), None)
        if not retry_trait:
            return

        if any(isinstance(t, Cancelled) for t in task.traits):
            return  # Do not retry tasks that have been cancelled (e.g., by timeout).

        if retry_trait.tries < retry_trait.max_tries:
            retry_trait.tries += 1
            # Use the new trait helpers to robustly manage the traits list.
            task.remove_traits_by_type(UncountedTrait, GeneratedTrait)
            task.replace_trait(retry_trait)
            task.replace_trait(RetryingTrait())
            backoff_delay = float(RetryableSystem._backoff(retry_trait))
            worker.log(
                f"Task {task.id} failed, scheduling retry {retry_trait.tries}/{retry_trait.max_tries} in {backoff_delay:.2f}s.",
                logging.INFO,
            )
            retry_at = worker.get_time() + backoff_delay
            await worker.add_task_for_retry(retry_at, task)

        else:
            # All retries have been exhausted. Mark the task as terminally failed so
            # that the worker's execute_task loop sends a `fail` result.
            task.replace_trait(Failed())
            worker.log(
                f"Task {task.id} failed after exhausting all {retry_trait.max_tries} retries.",
                logging.WARNING,
            )


class TimeoutSystem(BaseSystem):
    """System that adds a timeout to a task's execution."""

    required_traits: ClassVar[List[Type[BaseTrait]]] = [TimeoutTrait, Cancelled]

    @staticmethod
    @priority(500)
    async def around_task_execution(
        task: "Task",
        worker: "Worker",
        execution_callable: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Wraps the task execution with asyncio.wait_for."""
        timeout_trait = next((t for t in task.traits if isinstance(t, TimeoutTrait)), None)
        if not timeout_trait:
            return await execution_callable()

        try:
            return await asyncio.wait_for(execution_callable(), timeout_trait.timeout)
        except asyncio.TimeoutError as e:
            task.replace_trait(Cancelled())
            raise e
