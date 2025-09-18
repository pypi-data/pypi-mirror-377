# ECS Refactoring Plan: Migrating to Data-Only Traits and Systems

## Goal

The current architecture, where "Traits" contain both state and logic (methods/hooks), has proven to be fragile. Mutating a trait's state across different processes has led to subtle bugs, silent crashes, and an inconsistent system state.

The goal of this refactoring is to migrate to an **Entity-Component-System (ECS)** architecture. This will create a clear separation between data and logic, making the framework more robust, predictable, and easier to debug.

## Core Concepts

*   **Components (formerly Traits):** Traits will be refactored into pure data containers. They will be simple Pydantic models that define configuration and state (e.g., `max_retries`, `current_tries`). They will have no methods.
*   **Systems:** All logic currently in trait hooks (`on_task_success`, etc.) will be moved into stateless `System` classes. These systems will contain static methods that operate on tasks and their components.
*   **OrchestratorBuilder:** This will become the central point for registering **Systems**. It will be responsible for inspecting these systems to automatically discover and register their required **Component** data models.
*   **Worker:** The worker will become a "System Runner." It will no longer call methods on traits. Instead, at each lifecycle event, it will execute a list of registered system functions.

---

## Plan

### Step 1: Create `systems.py` and `BaseSystem`

The foundation of the new architecture is the `BaseSystem` class.

1.  Create a new file: `src/wombat/multiprocessing/systems.py`.
2.  In this file, define the `BaseSystem` class. This class links a system's logic to its required data components.

    ```python
    # In src/wombat/multiprocessing/systems.py
    from __future__ import annotations
    from typing import TYPE_CHECKING, ClassVar, List, Type

    if TYPE_CHECKING:
        from wombat.multiprocessing.traits.models import BaseTrait

    class BaseSystem:
        """Base class for all systems."""
        # A system declares the data components it operates on.
        required_traits: ClassVar[List[Type[BaseTrait]]] = []
    ```

### Step 2: Migrate All Traits to Components and Systems

This process must be repeated for **every single trait** in the `src/wombat/multiprocessing/traits/` directory. We will use `Retryable` as the primary example.

#### Before: Stateful `Retryable` Trait

```python
# In src/wombat/multiprocessing/traits/retryable.py (OLD VERSION)
class Retryable(BaseTrait):
    trait_name: Literal["retryable"] = "retryable"
    tries: int = 0
    max_tries: int = 3
    # ... other fields ...

    async def on_task_failure(self, task: "Task", worker: "Worker", ...):
        # ... complex logic to handle retries ...
        # ... mutates self.tries ...
        # ... adds a Retrying marker trait to the task ...
```

#### After: Data-only `RetryableTrait` and Stateless `RetryableSystem`

1.  **Refactor the Trait:** Rename the class to `RetryableTrait` and remove all methods, leaving only Pydantic fields.

    ```python
    # In src/wombat/multiprocessing/traits/retryable.py (NEW VERSION)
    class RetryableTrait(BaseTrait):
        """Data component for retry behavior."""
        trait_name: Literal["retryable"] = "retryable"
        tries: int = 0
        max_tries: int = 3
        # ... other fields ...
        # NO METHODS
    ```

2.  **Create the System:** Create a corresponding `RetryableSystem` in `systems.py` and move the logic there.

    ```python
    # In src/wombat/multiprocessing/systems.py
    from .traits.retryable import RetryableTrait
    # ... other necessary imports ...

    class RetryableSystem(BaseSystem):
        # Declare the data component this system needs.
        required_traits = [RetryableTrait]

        @staticmethod
        async def on_task_failure(task: "Task", worker: "Worker", exception: Exception | str | None):
            """Schedules a retry if the task has the RetryableTrait and tries remain."""
            # 1. The system first checks if the task has the component it operates on.
            retry_trait = next((t for t in task.traits if isinstance(t, RetryableTrait)), None)
            if not retry_trait:
                return  # This system does not apply to this task.

            # 2. The rest of this is the logic moved directly from the old hook.
            if retry_trait.tries < retry_trait.max_tries:
                retry_trait.tries += 1
                task.replace_trait(Retrying()) # Add a marker state trait
                # ... rest of the retry logic ...
    ```

**This migration must be performed for all traits:** `Accounting`, `Breaker`, `Debounce`, `Delayed`, `Evaluatable`, `Expirable`, `LifecycleManager`, `Loggable`, `Pinned`, `Produces`, `RateLimit`, and `Timeout`.

### Step 3: Update `OrchestratorBuilder`

The builder's API must change to reflect the new architecture.

1.  **Remove `.with_custom_traits()`:** This method is no longer needed, as traits are now an implementation detail of systems.
2.  **Add `.with_systems()`:** This will be the new primary method for adding functionality.
3.  **Update the `.build()` method:**
    *   It will iterate over the systems registered via `.with_systems()`.
    *   For each system, it will inspect `system.required_traits` and add those trait classes to a set of all required traits.
    *   This set will be used to build the `trait_registry` for deserialization.
    *   It will inspect each registered system for `staticmethod`s that match the lifecycle hook names (e.g., `on_task_failure`).
    *   It will build a `system_registry` dictionary that maps event names to a list of system functions (e.g., `{"on_task_failure": [RetryableSystem.on_task_failure, ...]}`). This registry will be passed to the workers.

### Step 4: Rewrite `Worker.execute_task`

The worker's core execution loop will be completely rewritten to be a stateless system runner.

#### Before: Calling Hooks on Traits

```python
# In src/wombat/multiprocessing/worker.py (OLD VERSION)
# Conceptual example:
try:
    result = await task_action()
    for trait in task.traits:
        await trait.on_task_success(task, self, result)
except Exception as e:
    for trait in task.traits:
        await trait.on_task_failure(task, self, e)
```

#### After: Executing Registered Systems

```python
# In src/wombat/multiprocessing/worker.py (NEW VERSION)
# Conceptual example:
try:
    result = await task_action()
    # Look up and execute all registered systems for the "on_task_success" event.
    if "on_task_success" in self.system_registry:
        for system_func in self.system_registry["on_task_success"]:
            await system_func(task, self, result)
except Exception as e:
    if "on_task_failure" in self.system_registry:
        for system_func in self.system_registry["on_task_failure"]:
            await system_func(task, self, e)
```

### Step 5: Update Public API and Tests

1.  **Decorators:** All decorators (`@retryable`, `@timeout`, etc.) must be updated to apply the new data-only `*Trait` classes (e.g., `@retryable` will add a `RetryableTrait` instance).
2.  **`__init__.py`:** The main `wombat.multiprocessing.__init__.py` must be updated to export the new `System` classes and `*Trait` data classes.
3.  **Tests and Examples:** All test files and examples must be updated. Any instance of `.with_custom_traits([...])` must be replaced with `.with_systems([...])`.

    **Example Test Fixture Change:**

    *Before:*
    ```python
    builder = OrchestratorBuilder().with_custom_traits([Retryable, Timeout])
    ```

    *After:*
    ```python
    builder = OrchestratorBuilder().with_systems([RetryableSystem, TimeoutSystem])
    ```
