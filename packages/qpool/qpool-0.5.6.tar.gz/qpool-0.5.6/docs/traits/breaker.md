# Breaker Trait

Implements the Circuit Breaker pattern to prevent repeated failures against a shared resource. It transitions between CLOSED, OPEN, and HALF_OPEN states based on task success and failure.

```mermaid
graph TD
    subgraph "Worker Lifecycle"
        A[on_before_execute] --> B{Circuit OPEN?};
        B -->|No| E[Execute Task Action];
        B -->|Yes| C{Recovery Timeout Passed?};
        C -->|No| D[Block Execution & Fail Task];
        C -->|Yes| D2[Set Circuit to HALF_OPEN];
        D2 --> E;

        E --> F{Task Succeeded?};
        F -->|Yes| G[on_success];
        G --> H{Circuit HALF_OPEN?};
        H -->|Yes| I[Reset Failures & CLOSE Circuit];
        H -->|No| J[End];
        F -->|No| K[on_failure];
        K --> L{Failure Threshold Met?};
        L -->|Yes| M[OPEN Circuit];
        L -->|No| N[Increment Failures];
    end

    subgraph "Builder Lifecycle"
        O[on_build] --> P["Inject Shared State Props<br/>(breaker_lock, breaker_states)"];
    end
```
