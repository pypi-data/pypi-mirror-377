# Loggable Trait

Enables automatic logging of a task's lifecycle events (e.g., start, finish, fail) and allows for customization of the log level. All log messages are processed by a dedicated logging worker. Manual logging within a task's action can be performed using the worker.log() method.

```mermaid
graph TD
    subgraph "Task Worker (with @loggable)"
        A[Lifecycle Hook Triggered] --> B{"e.g., on_success, on_failure"};
        B --> C["Loggable trait creates new Log Task"];
        C --> D[Put Log Task on Log Queue];
    end

    subgraph Log Worker
        E[Get Log Task from Queue] --> F["Execute 'log' action"];
        F --> G["Write to file/console"];
    end
```
