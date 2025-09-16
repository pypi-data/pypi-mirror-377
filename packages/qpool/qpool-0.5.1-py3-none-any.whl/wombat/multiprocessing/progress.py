# File: src/wombat/multiprocessing/progress.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple

from pydantic import BaseModel
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TimeElapsedColumn,
)
from rich.progress import (
    Task as RichTask,
)
from rich.table import Column
from rich.text import Text

if TYPE_CHECKING:
    pass


class ProgressConfig(BaseModel):
    """Configuration for the progress bar display."""

    enabled: bool = False


def tasks_per_second_from_task(task: RichTask, precision: int) -> Optional[float]:
    """Calculates the tasks per second from a rich Task object."""
    if not task or (not task.elapsed) or (task.elapsed == 0):
        return None

    return round(
        0 if task.completed == 0 else (task.completed / task.elapsed),
        precision,
    )


class TimeRemainingColumn(ProgressColumn):
    """Renders estimated time remaining for a rich progress task."""

    max_refresh = 0.5

    def __init__(self, compact: bool = False, table_column: Optional[Column] = None):
        self.compact = compact
        super().__init__(table_column=table_column)

    def render(self, task: RichTask) -> Text:
        """Show time remaining."""
        style = "progress.remaining"

        if (
            not task
            or not task.total
            or task.total == 0
            or not task.completed
            or task.completed == 0
            or not task.elapsed
            or task.elapsed == 0
        ):
            return Text("--:--" if self.compact else "-:--:--", style=style)

        tasks_per_second: float | None = tasks_per_second_from_task(task, 2)

        if not tasks_per_second:
            return Text("--:--" if self.compact else "-:--:--", style=style)

        remaining_tasks: int = int(task.total - task.completed)

        estimated_time_remaining = remaining_tasks / tasks_per_second
        minutes, seconds = divmod(round(estimated_time_remaining), 60)
        hours, minutes = divmod(minutes, 60)

        if self.compact and not hours:
            formatted = f"{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{hours:d}:{minutes:02d}:{seconds:02d}"

        return Text(formatted, style=style)


class ItemsPerMinuteColumn(ProgressColumn):
    """Renders tasks per minute for a rich progress task."""

    max_refresh = 0.5

    def __init__(self, precision: int = 2, table_column: Optional[Column] = None):
        super().__init__(table_column=table_column)
        self.precision = precision

    def render(self, task: RichTask) -> Text:
        """Show tasks per minute."""
        style = "progress.remaining"

        if not task or (not task.elapsed) or (task.elapsed == 0):
            return Text("?/m", style=style)

        tasks_per_second = tasks_per_second_from_task(task, self.precision)
        if tasks_per_second is None:
            return Text("?/m", style=style)

        tasks_per_minute = tasks_per_second * 60
        return Text(f"{tasks_per_minute:.2f}/m", style=style)


def create_progress_bars(num_bars: int) -> Tuple[Progress, list[TaskID]]:
    """
    Creates a `rich.progress.Progress` instance with a set of predefined columns
    and adds a progress bar for each worker.

    Args:
        num_bars: The number of worker progress bars to create.

    Returns:
        A tuple containing the Progress instance and a list of TaskIDs for each bar.
    """
    console = Console(stderr=True)
    progress_bar = Progress(
        SpinnerColumn(),
        "{task.fields[status]}...",
        BarColumn(),
        "{task.fields[finished]} of {task.total}",
        "[blue]📥: {task.fields[initial]}",
        "[green]🌱: {task.fields[generated]}",
        "[red]❌: {task.fields[failures]}",
        "[yellow]🔃: {task.fields[retries]}",
        "[cyan]↪️: {task.fields[skipped]}",
        "[magenta]🛑: {task.fields[cancelled]}",
        "[grey]⌛: {task.fields[expired]}",
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        ItemsPerMinuteColumn(),
        console=console,
        auto_refresh=False,
    )
    tasks: list[TaskID] = []
    for bar in range(num_bars):
        tasks.append(
            progress_bar.add_task(
                description=f"Worker-{bar}",
                start=True,
                total=0,
                completed=0,
                visible=True,
                status="Starting...",
                failures=0,
                retries=0,
                generated=0,
                initial=0,
                finished=0,
                skipped=0,
                cancelled=0,
                expired=0,
            )
        )
    return progress_bar, tasks


def _update_progress_bars(
    progress_bar: Progress,
    task_ids: list[TaskID],
    total_task_id: TaskID,
    accounting_store: Mapping,
):
    """
    Updates all progress bars with the latest data from the accounting store.

    This function is the consumer of the accounting system. It reads the shared
    dictionary but does not write to it.
    """
    # Use a non-blocking lock to prevent deadlocks with workers. If the lock
    # is held, we skip this update cycle.
    if not accounting_store.lock.acquire(block=False):
        return

    try:
        data = accounting_store._read_data()
    finally:
        accounting_store.lock.release()

    total_counts = data.get("Total", {})
    total_initial = total_counts.get("initial", 0)
    total_generated = total_counts.get("generated", 0)
    total_tasks = total_initial + total_generated

    for i, task_id in enumerate(task_ids):
        worker_key = f"worker-{i}"
        worker_counts = data.get(worker_key, {})

        w_initial = worker_counts.get("initial", 0)
        w_generated = worker_counts.get("generated", 0)
        w_completed = worker_counts.get("completed", 0)
        w_failures = worker_counts.get("failures", 0)
        w_retries = worker_counts.get("retries", 0)
        w_skipped = worker_counts.get("skipped", 0)
        w_cancelled = worker_counts.get("cancelled", 0)
        w_expired = worker_counts.get("expired", 0)

        w_total = w_initial + w_generated
        w_finished = w_completed + w_failures + w_skipped + w_cancelled + w_expired

        progress_bar.update(
            task_id,
            total=w_total,
            completed=w_finished,
            finished=w_finished,
            failures=w_failures,
            retries=w_retries,
            generated=w_generated,
            initial=w_initial,
            skipped=w_skipped,
            cancelled=w_cancelled,
            expired=w_expired,
            refresh=True,
        )

    # Update the "Total" bar
    total_completed = total_counts.get("completed", 0)
    total_failures = total_counts.get("failures", 0)
    total_retries = total_counts.get("retries", 0)
    total_skipped = total_counts.get("skipped", 0)
    total_cancelled = total_counts.get("cancelled", 0)
    total_expired = total_counts.get("expired", 0)
    total_finished = (
        total_completed + total_failures + total_skipped + total_cancelled + total_expired
    )
    total_status = "Running..."  # TODO: get from orchestrator

    progress_bar.update(
        total_task_id,
        total=total_tasks,
        completed=total_finished,
        finished=total_finished,
        failures=total_failures,
        retries=total_retries,
        generated=total_generated,
        initial=total_initial,
        status=total_status,
        skipped=total_skipped,
        cancelled=total_cancelled,
        expired=total_expired,
        refresh=True,
    )


def run_progress(
    num_bars: int,
    progress_ipc: dict[str, Any],
    capture_dict: Mapping | None = None,
):
    """
    The main function for the progress bar process.

    It creates and manages the progress display, updating it periodically based
    on signals from the orchestrator and data from the shared accounting store.

    Args:
        num_bars: The number of worker bars to display.
        progress_ipc: A dictionary containing IPC objects for synchronization
                      (stop_event, update_event) and the accounting_store.
        capture_dict: An optional dictionary to capture final metrics, used for testing.
    """
    progress_bar, task_ids = create_progress_bars(num_bars=num_bars)
    total_task_id = progress_bar.add_task(
        description="Total",
        start=True,
        total=0,
        completed=0,
        visible=True,
        status="Starting...",
        failures=0,
        retries=0,
        generated=0,
        initial=0,
        finished=0,
        skipped=0,
        cancelled=0,
        expired=0,
    )

    stop_event = progress_ipc["stop_event"]
    update_event = progress_ipc["update_event"]
    accounting_store = progress_ipc["accounting_store"]

    progress_bar.start()
    try:
        while not stop_event.is_set():
            _update_progress_bars(
                progress_bar, task_ids, total_task_id, accounting_store
            )
            # Wait for a signal to update progress, with a timeout for periodic refresh.
            update_event.wait(timeout=0.1)
            update_event.clear()

    except (OSError, ValueError):
        # These can happen during shutdown, it's safe to exit.
        pass
    finally:
        # This block must be extremely robust, as it runs during shutdown when
        # other components may be in a partially-terminated state.

        # 1. First, try to perform a final update to catch any last-minute changes.
        # This may fail if the rich.progress object is in a bad state, so we wrap it.
        try:
            _update_progress_bars(
                progress_bar, task_ids, total_task_id, accounting_store
            )
        except Exception:
            # It's safe to ignore this exception, as the primary goal is metric capture.
            pass

        # 2. Capture metrics directly from the accounting store. This is the
        # most critical part and must be protected.
        if capture_dict is not None:
            try:
                # Use a blocking lock with a short timeout to prevent deadlocks during shutdown.
                if accounting_store.lock.acquire(timeout=0.1):
                    try:
                        data = accounting_store._read_data()
                        for key, value in data.items():
                            capture_dict[key] = value
                    finally:
                        accounting_store.lock.release()
            except Exception:
                # If metric capture itself fails, we can't do much, but we
                # still want to ensure the progress bar is stopped.
                pass

        # 3. Finally, stop the progress bar, also wrapped for safety.
        try:
            progress_bar.stop()
        except Exception:
            pass
