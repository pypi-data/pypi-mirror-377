# QPool

## Description

Multiprocessing with Process Pools implemented using Processes and Shared Memory objects.

- Built in progress bar.
- Traits for rate-limiting, exponential backoff and retry, logging, and more.
- Graceful shutdown by default (CTRL+C 2x, will kill immediately).- Allows re-use of pool after join, cutting down on process spawning time.

# Debugging Tips
- If hanging, investigate stop_workers, specifically the point of joining the processes, unclosed queues and resources can prevent process closure.

# Progress Icons

 • 📥 initial: Tasks submitted directly by the user.
 • 🌱 generated: Tasks produced by other tasks.
 • 📜 logs: Internal tasks created for logging messages.
 • ❌ failures: Tasks that failed after all retries were exhausted.
 • 🔃 retries: Tasks that failed and were scheduled for a retry.
 • ↪ skipped: Tasks that were skipped (e.g., by the debounce trait).
 • 🛑 cancelled: Tasks that were cancelled (e.g., by the timeout trait).
 • ⌛ expired: Tasks that expired before they could be executed.