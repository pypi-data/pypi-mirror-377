# Logging and LogCarrier Trait

Wombat provides a robust, non-blocking logging system that funnels all log messages through a dedicated worker process. This ensures that I/O operations from logging do not impact the performance of your task workers.

## Manual Logging with `worker.log()`

The primary way to log from within a task action is to use the `worker.log()` method, which is available on the `worker` object passed to every task action.

```python
from wombat.multiprocessing import task, Worker
import logging

@task
def my_logging_task(worker: Worker):
    worker.log("This is an info message.", logging.INFO)
    worker.log("This is a debug message.", logging.DEBUG)
```

Calling `worker.log()` creates a special, internal `log_task` and sends it to the orchestrator, which then routes it to a dedicated log worker.

## `LogCarrierTrait`

The `LogCarrierTrait` is an internal trait automatically applied to the `log_task` created by `worker.log()`. Its primary purpose is to prevent logging cycles.

If a `log_task` itself were to fail, the system might try to log that failure, creating another `log_task`, which could also fail, leading to an infinite loop. The `LogCarrierTrait` has two key properties:

1.  It prevents failure-logging hooks from running for any task that has this trait.
2.  It ensures the log task is correctly counted in the `logs` metric for progress tracking.

This trait is not intended for direct use by users.
