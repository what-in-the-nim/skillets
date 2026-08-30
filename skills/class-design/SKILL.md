---
name: class-design
description: Apply whenever designing, modifying, or reviewing a class.
---

# Class Design

Apply these principles when designing, modifying, or reviewing a class. Make classes cohesive, hard to misuse, and safe throughout their lifecycle.

## Core Principle

A good class owns one coherent concept, maintains its invariants, controls its lifecycle, and exposes only the interface needed to use it correctly.

## Design Rules

### 1. Single Responsibility

Give the class one clear responsibility. Split unrelated responsibilities into separate classes.

### 2. High Cohesion

Keep fields and methods focused on the same concept. Separate groups that operate on mostly independent state.

### 3. Minimal Public Interface

Expose only necessary operations. Prefer high-level methods over caller-coordinated implementation steps. Each public method or mutable property adds states and misuse paths.

### 4. Make Invalid States Hard to Represent

Prevent contradictory combinations with explicit states or constrained representations instead of loosely related booleans. Identify valid states and transitions for non-trivial lifecycles.

### 5. Explicit Lifecycle

For stateful or resource-owning classes, define when the object is usable, its states and valid transitions, allowed operations, cleanup, and initialization or shutdown failure behavior. Make ownership visible in the API.

### 6. Idempotent Lifecycle Operations

Repeated `close()`, `stop()`, `cancel()`, cleanup, or unsubscribe calls should be safe: no corruption, leaks, or races.

### 7. Protect Invariants Internally

The class must maintain its own correctness. Encapsulate operations that must happen together behind a higher-level method instead of relying on caller sequencing.

### 8. Encapsulate Implementation Details

Keep queues, locks, tasks, counters, transports, caches, and similar mechanisms private unless callers genuinely need them.

### 9. Explicit Dependencies

Expose significant dependencies through constructors or deliberate injection points. Avoid silently constructing dependencies when it obscures configuration, testing, replacement, or ownership.

### 10. Minimize Temporal Coupling

Avoid undocumented sequences such as `initialize → prepare → start → read → stop → cleanup`. Simplify required ordering, enforce it through the API, or represent it with lifecycle states.

### 11. Consistent Abstraction Level

Keep methods at similar abstraction levels. Delegate parsing, protocol handling, serialization, persistence, and other low-level work to appropriate components.

### 12. Prefer Composition

Compose small, explicit components instead of building deep inheritance hierarchies. Use inheritance for genuine substitutability, not implementation reuse alone.

### 13. Explicit Concurrency Ownership

For concurrent or asynchronous classes, define who creates, owns, cancels, and awaits each task; how failures propagate; whether concurrent operations are allowed; how lifecycle races are handled; and whether tasks may outlive the object. Components that create background work should participate in cleanup.

### 14. Preserve Invariants on Failure

Every operation must leave a defined, valid state on partial initialization or shutdown, cancellation, timeout, or transition failure. Avoid ambiguous half-initialized or half-closed states.

### 15. Justify the Class

Introduce a class only when it provides meaningful state, identity, invariants, lifecycle or resource ownership, encapsulation, polymorphism, or cohesive behavior. Otherwise prefer functions or modules.

## Review Priority

Evaluate issues in this order: ownership; valid states and invariants; lifecycle; concurrency; failure and cancellation; idempotency; cohesion and responsibility; public interface; dependencies; abstraction and implementation structure. Prioritize correctness and misuse prevention over stylistic purity.

## Review Questions

Ask:

- What concept, state, and invariants does this class own?
- What are its valid lifecycle states, transitions, and allowed operations?
- Can callers create invalid states or call methods in the wrong order?
- Are cleanup and cancellation safe when repeated or interrupted?
- Who owns resources and background tasks, and what happens on failure?
- Are dependencies, ownership boundaries, and concurrency rules explicit?
- Are the interface, fields, and methods larger or less cohesive than necessary?
- Would composition simplify the design?
- Does this need to be a class?

## Review Finding Format

For each problem, report:

1. **Rule** — name and number of the violated design rule.
2. **Failure mode** — the concrete misuse, invalid state, lifecycle bug, or other failure enabled.
3. **Smallest reproducible example** — minimal code that demonstrates the problem.
4. **Proposed remedy** — after reviewing all findings together, identify any shared root cause. If a better overall class design is justified, propose it; otherwise give a focused change.

Keep each example focused on one finding.

## Design Synthesis

Assess the complete set of findings before choosing remedies. Treat recurring problems involving ownership, state, interface size, responsibilities, dependencies, lifecycle, or concurrency as evidence of a shared design flaw rather than isolated defects.

When a redesign is justified, describe:

- The concept and responsibility the class should own.
- Its explicit state and invariants.
- Its public interface and dependencies.
- Its lifecycle, resource ownership, and concurrency boundaries.
- How the design addresses each related finding.

Use a focused fix when findings are independent or redesign would add complexity without improving correctness. Do not force theoretical abstractions.
