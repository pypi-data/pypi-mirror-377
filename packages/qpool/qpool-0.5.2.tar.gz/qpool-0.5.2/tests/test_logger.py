import logging
import os
import tempfile

import pytest
import pytest_check as check

from wombat.multiprocessing import OrchestratorBuilder
from wombat.multiprocessing.logging import setup_logging
from wombat.multiprocessing.traits.models import TaskDefinition
from wombat.multiprocessing.worker import Worker

# --- Test setup_logging ---


@pytest.mark.timeout(5)
def test_setup_logging_defaults():
    """Tests that setup_logging works with default arguments."""
    # Use a unique name to avoid conflicts with other tests
    logger = setup_logging(name="test_default")
    check.equal(logger.level, logging.ERROR)
    check.is_true(any(isinstance(h, logging.FileHandler) for h in logger.handlers))
    # Cleanup handlers to not affect other tests
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


@pytest.mark.timeout(5)
def test_setup_logging_with_args():
    """Tests that setup_logging respects passed arguments."""
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        logger = setup_logging(
            name="test_args",
            level=logging.DEBUG,
            log_file=tmp.name,
            to_console=True,
            max_bytes=100,
            backups=1,
        )
        check.equal(logger.level, logging.DEBUG)
        check.is_true(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        )
        file_handler = next(
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        )
        check.equal(file_handler.baseFilename, tmp.name)
        check.equal(file_handler.maxBytes, 100)
        check.equal(file_handler.backupCount, 1)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()


@pytest.mark.timeout(5)
def test_setup_logging_env_overrides():
    """Tests that environment variables correctly override defaults."""
    old_env = os.environ.copy()
    os.environ["WOMBAT_LOG_LEVEL"] = "INFO"
    os.environ["WOMBAT_LOG_STDOUT"] = "true"
    os.environ["WOMBAT_LOG_MAX"] = "200"
    os.environ["WOMBAT_LOG_BACKUPS"] = "3"

    try:
        logger = setup_logging(name="test_env")
        check.equal(logger.level, logging.INFO)
        check.is_true(
            any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        )
        file_handler = next(
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        )
        check.equal(file_handler.maxBytes, 200)
        check.equal(file_handler.backupCount, 3)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
    finally:
        os.environ.clear()
        os.environ.update(old_env)


@pytest.mark.timeout(5)
def test_setup_logging_idempotency():
    """Tests that calling setup_logging multiple times doesn't add duplicate handlers."""
    logger = setup_logging(name="test_idempotent", to_console=True)
    initial_handler_count = len(logger.handlers)
    setup_logging(name="test_idempotent", to_console=True)
    check.equal(len(logger.handlers), initial_handler_count)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


# --- E2E Test ---


def log_action(worker: Worker, message: str, level: int):
    """A task that uses the worker's log method."""
    worker.log(message, level)


log_message_task = TaskDefinition(
    action=log_action,
    action_name=f"{log_action.__module__}.{log_action.__name__}",
)


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_e2e_logging():
    """
    Tests the full end-to-end logging pipeline:
    1. A task worker calls `worker.log()`.
    2. This creates a `log_task` and sends it to the orchestrator's requeue.
    3. The orchestrator routes the `log_task` to the dedicated log worker.
    4. The log worker executes the task, writing the message to a file.
    5. The test verifies the file content after the orchestrator shuts down.
    """
    log_file_path = ""
    try:
        # Use mkstemp to avoid race conditions and have more control over the file.
        fd, log_file_path = tempfile.mkstemp(suffix=".log")
        os.close(fd)

        logging_config = {
            "log_file": log_file_path,
            "level": logging.INFO,
            "to_console": False,
        }

        builder = (
            OrchestratorBuilder()
            .with_workers(num_workers=1)
            .with_actions([log_message_task])
            .with_logging(logging_config)
        )

        test_message = "This is an end-to-end test log message."
        async with builder.build() as orchestrator:
            await orchestrator.add_task(
                log_message_task(message=test_message, level=logging.INFO)
            )
            # We must wait for the main task to finish, which is what triggers the log task.
            await orchestrator.finish_tasks()

            # We also need to wait for the log task to be processed.
            # finish_tasks only waits for tasks added via add_tasks.
            # The log_task is added dynamically to the requeue.
            # The graceful shutdown will wait for the requeue to drain and log workers to finish.
            # So, exiting the `async with` is the correct way to ensure logs are flushed.

        with open(log_file_path) as f:
            log_content = f.read()

        check.is_in(test_message, log_content)
        check.is_in("worker=worker-0", log_content)
        check.is_in("INFO", log_content)

    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
