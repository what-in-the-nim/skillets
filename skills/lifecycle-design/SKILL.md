---
name: lifecycle-design
description: Apply when designing new code that introduces stateful objects, resources, services, workers, sessions, connections, background tasks, or concurrent components.
---

# Object Lifecycle Design

Apply when designing new code that introduces stateful objects, resources, services, workers, sessions, connections, background tasks, or concurrent components.

## Goal

Make behavior easy to reason about throughout an object's entire lifetime, including initialization, normal operation, failure, concurrency, cleanup, and destruction.

## Principles

### Minimize State

Every mutable field increases the possible state space.

- Prefer small, cohesive objects.
- Avoid redundant or correlated state.
- Derive values instead of storing them when practical.
- Prefer one explicit lifecycle state over multiple related booleans.

Ask: **Can this object represent a state that should never exist?**

If yes, simplify or redesign the representation.

### Make Lifecycle Explicit

For meaningful lifecycle complexity, identify:

- possible states
- valid transitions
- terminal states
- operations allowed in each state

Prefer explicit state machines over lifecycle encoded implicitly across unrelated fields.

Example: `CREATED → STARTING → RUNNING → STOPPING → CLOSED`

### Preserve Invariants

Make invalid states difficult or impossible to represent.

Prefer APIs and structures that enforce invariants rather than relying on callers to remember rules.

Fail early on illegal operations or transitions.

### Define Ownership

Every stateful resource should have a clear owner.

Determine who:

- creates it
- mutates it
- starts/stops it
- cleans it up
- may transfer ownership

Prefer few actors controlling lifecycle transitions.

### Prefer Structured Lifetime

Tie resource lifetime to scope where possible using mechanisms such as context managers, `try/finally`, task groups, or explicit parent-child ownership.

Cleanup should not depend on callers remembering an unrelated future action.

### Make Cleanup Idempotent

Where practical, repeated cleanup should be harmless.

Typical candidates: `close()`, `stop()`, `cancel()`, `disconnect()`, and `release()`.

Idempotency reduces coordination requirements but does not by itself provide concurrency safety.

### Treat Concurrency as Lifecycle

Assume state may change whenever control is yielded.

Review lifecycle transitions across `await`, callbacks, threads, event handlers, and background tasks.

Protect transitions requiring atomicity, or preferably reduce shared mutable ownership.

## Design Review

When designing stateful code, check:

1. **State** — Can mutable state be reduced?
2. **Invariants** — Can invalid combinations exist?
3. **Lifecycle** — Are valid states and transitions clear?
4. **Ownership** — Who controls and destroys the object?
5. **Cleanup** — Is cleanup guaranteed and preferably idempotent?
6. **Concurrency** — Can transitions race or become stale?
7. **Failure** — What state remains after partial failure?
8. **API** — Does the interface prevent misuse?

Prefer:

**Few states + few transitions + few actors controlling transitions.**

Avoid lifecycle machinery for effectively stateless objects or when it adds complexity without meaningful safety.
