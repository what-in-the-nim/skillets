# Example: give retry decisions one owner

Illustrative proposal only; this does not report a confirmed runtime defect.

## Recommendation

Move retry-limit and backoff decisions from `Worker` into `RetryPolicy`. The worker keeps attempt execution and result delivery; the retry rule becomes independently testable.

## Before and target

### Before

```mermaid
flowchart LR
    Request --> Attempt[Worker runs attempt]
    Attempt --> Result{Succeeded?}
    Result -->|Yes| Complete[Return result]
    Result -->|No| Decide[Worker checks limit and backoff]
    Decide -->|Retry| Wait[Wait]
    Wait --> Attempt
    Decide -->|Stop| Failed[Return failure]
```

### Target

```mermaid
flowchart LR
    Request --> Attempt[Worker runs attempt]
    Attempt --> Result{Succeeded?}
    Result -->|Yes| Complete[Return result]
    Result -->|No| Call[Worker requests retry delay]
    Call --> Policy{RetryPolicy applies limit and backoff}
    Policy -->|Delay| Wait[Worker waits]
    Wait --> Attempt
    Policy -->|Stop| Failed[Return failure]
```

## Target design

- `Worker` owns attempt execution, waiting, and result delivery.
- `RetryPolicy.next_delay(result, attempt)` returns a delay or `None` when retries stop.

## Evidence and validation

- **Proposed improvement:** isolated policy tests can avoid constructing the worker. This example has no source evidence.
- **Proposed check:** cover retry just below, at, and above the attempt limit; keep one integration check for retry ordering.

## First PR

- Add `RetryPolicy` and route one worker through its narrow interface.
- Preserve attempt limits, backoff, and failure propagation; defer other callers.
