---
name: class-design
description: Apply whenever designing, modifying, or reviewing a class.
---

# Class Design

Apply these principles whenever designing, modifying, or reviewing a class. Focus on making classes easy to reason about, difficult to misuse, and safe throughout their lifecycle.

## Core Principle

A good class owns one coherent concept, maintains its invariants, controls its lifecycle, and exposes the smallest interface necessary to use it correctly.

## Design Rules

### 1. Single Responsibility

A class should have one clear responsibility that can be described in one short sentence.

Split classes that combine unrelated responsibilities.

### 2. High Cohesion

Fields and methods should strongly relate to the same concept.

If different groups of methods operate on mostly independent sets of state, consider separating them into different classes.

### 3. Minimal Public Interface

Expose only operations callers actually need.

Prefer high-level operations that encapsulate internal steps rather than requiring callers to coordinate implementation details.

Every additional public method or mutable property increases the number of possible object states and misuse paths.

### 4. Make Invalid States Hard to Represent

Design state so contradictory combinations cannot occur.

Prefer explicit state machines or constrained representations over multiple loosely related boolean flags.

Identify the valid states and transitions when an object has a non-trivial lifecycle.

### 5. Explicit Lifecycle

For stateful or resource-owning classes, determine:

- When the object becomes usable.
- Which lifecycle states exist.
- Which transitions are valid.
- What operations are allowed in each state.
- How shutdown and cleanup work.
- What happens when initialization or shutdown fails.

Lifecycle ownership should be obvious from the API.

### 6. Idempotent Lifecycle Operations

Operations such as `close()`, `stop()`, `cancel()`, cleanup, and unsubscribe should usually tolerate repeated calls.

Repeated cleanup should not corrupt state, leak resources, or introduce race conditions.

### 7. Protect Invariants Internally

The class is responsible for maintaining its own correctness.

Do not require callers to remember a fragile sequence of operations to keep the object valid.

If several internal operations must happen together, expose a higher-level operation that performs them correctly.

### 8. Encapsulate Implementation Details

Internal queues, locks, tasks, counters, transports, caches, and other implementation mechanisms should remain private unless callers genuinely need them.

Implementation changes should have minimal impact on callers.

### 9. Explicit Dependencies

Dependencies should be visible through constructors or other deliberate injection points.

Avoid silently constructing significant external dependencies inside the class when doing so makes configuration, testing, replacement, or ownership unclear.

### 10. Minimize Temporal Coupling

Avoid APIs where callers must know an undocumented sequence such as:

`initialize → prepare → start → read → stop → cleanup`

When ordering is necessary, simplify it, enforce it through the API, or represent it explicitly through lifecycle states.

### 11. Consistent Abstraction Level

Methods within a class should generally operate at similar abstraction levels.

High-level orchestration should delegate low-level parsing, protocol handling, serialization, persistence, and similar details to appropriate components.

### 12. Prefer Composition

Prefer combining small components with explicit responsibilities over creating deep inheritance hierarchies.

Use inheritance when there is a genuine substitutable abstraction, not merely to reuse implementation.

### 13. Explicit Concurrency Ownership

For concurrent or asynchronous classes, determine:

- Who creates each task.
- Who owns each task.
- Who cancels it.
- Who awaits it.
- How failures propagate.
- Whether concurrent operations are allowed.
- How races between lifecycle operations are handled.
- Whether tasks may outlive the object.

A component that creates background work should normally participate in its cleanup.

### 14. Preserve Invariants on Failure

Operations should leave the object in a defined, valid state even when they fail.

Pay particular attention to partial initialization, partial shutdown, cancellation, timeout, and exceptions during state transitions.

Avoid ambiguous half-initialized or half-closed states.

### 15. Justify the Class

Do not introduce a class merely to group functions.

A class should normally provide at least one meaningful benefit such as:

- State
- Identity
- Invariants
- Lifecycle management
- Resource ownership
- Encapsulation
- Polymorphism
- Cohesive behavior

Prefer ordinary functions or modules when none of these apply.

## Review Priority

When evaluating a class, prioritize issues in this order:

1. Ownership
2. Valid states and invariants
3. Lifecycle correctness
4. Concurrency safety
5. Failure and cancellation behavior
6. Idempotency
7. Cohesion and responsibility
8. Public interface size
9. Dependency boundaries
10. Abstraction and implementation structure

Prioritize correctness and misuse prevention over stylistic purity.

## Review Questions

Before accepting a design, ask:

- What concept does this class own?
- What state does it own?
- What invariants must always hold?
- What are its valid lifecycle states and transitions?
- Can callers construct or cause an invalid state?
- Can callers misuse the API by calling methods in the wrong order?
- Are cleanup operations safe when called multiple times?
- Who owns resources and background tasks?
- What happens when an operation fails halfway through?
- What happens during cancellation?
- Are dependencies and ownership boundaries explicit?
- Is the public API larger than necessary?
- Are all fields and methods genuinely cohesive?
- Would composition simplify the design?
- Does this need to be a class at all?

## Review Finding Format

For each problem found, report:

1. **Rule** — identify the violated design rule by name and number.
2. **Failure mode** — explain the concrete misuse, invalid state, lifecycle bug, or other failure the problem enables.
3. **Smallest reproducible example** — show the minimal code that demonstrates the problem and makes the failure easy to understand.
4. **Proposed remedy** — after considering all findings together, determine whether this problem shares a root cause with other issues. When a broader design problem is valid, propose a better class design that addresses the related problems together. Otherwise, recommend a focused change for this problem.

Keep each example focused on one finding. Avoid recommending abstractions solely for theoretical cleanliness.

## Design Synthesis

Review the complete set of findings before settling on remedies. When several problems arise from unclear ownership, invalid state combinations, excessive interface surface, tangled responsibilities, hidden dependencies, or unsafe lifecycle and concurrency design, treat them as evidence of a shared class-design problem rather than as isolated defects.

When a better overall design is justified, describe:

- The cohesive concept and responsibility the class should own.
- The state and invariants it should make explicit.
- The public interface and dependencies it should expose.
- The lifecycle, resource ownership, and concurrency boundaries it should control.
- How the proposed design addresses each related finding.

Use a focused fix when the findings are independent or when a redesign would add complexity without improving correctness. Do not force a redesign merely to make the code theoretically cleaner.
