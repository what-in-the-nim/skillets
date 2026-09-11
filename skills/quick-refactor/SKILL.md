---
name: quick-refactor
description: Propose a small refactor PR that improves encapsulation, abstraction, and testability, delivered as an HTML report with fixed sections and Mermaid diagrams. Use when the user asks for a quick refactor opportunity or a before-and-after refactor proposal.
---

# Quick Refactor

Find one cohesive responsibility whose ownership and tests can improve in a small PR. Preserve behavior and public contracts.

## Trace

- Read repo instructions and status; preserve unrelated work.
- Inspect the target, constructor, callers, wiring, collaborators, and tests. Verify the current code.
- Trace state, dependencies, side effects, and lifecycle. For async resources, identify who creates, awaits, cancels, and closes them.
- Note oversized test graphs and private-field assertions.

Done when exact source locations support the candidate's behavior, dependencies, lifecycle, and tests.

## Bound

- Prefer an existing owner; add a class only for state, invariants, or lifecycle. Use functions for stateless work.
- Give the new owner a narrow interface and dependencies, not the whole worker or callback bag.
- Compare at most two options; recommend the smallest useful one, or say none exists.
- Keep policy with its domain owner. Separate bug fixes and behavior changes from the refactor.

Done when responsibility, dependencies, files, and tests are bounded.

## Own

Show what moves: methods, state, duplicates, interface, caller duties, ordering, resources, failures, cancellation, and reusable teardown guarantees. Every affected behavior and state must have one owner; the interface must be testable without the original large object.

## Render

Create one-string-per-token JSON for [templates/proposal.html](templates/proposal.html). `_HTML` tokens are trusted fragments; all others are text. For each Mermaid token, use `@relative/path.mmd` so diagrams stay out of JSON. Keep the template unchanged.

Write separate `.mmd` files for current/proposed structure and current/proposed workflow. Use valid `classDiagram` for structure and `sequenceDiagram` for both workflows.

Run from the project root:

```sh
python skills/quick-refactor/scripts/render_proposal.py proposal.json --output <report-path>
```

Add `--check-mermaid` when `mmdc` is installed; it validates all four diagrams and reports when the tool is unavailable. The renderer loads referenced Mermaid files relative to `proposal.json`, escapes text and Mermaid, rejects missing or unknown tokens, and substitutes once. Lead with the recommendation and source evidence. Include failure, timeout, and cancellation paths. For function-only changes, use flowcharts and explain why.

Keep the report glanceable: lead with the recommendation, then paired current/proposed diagrams, then changes. Put supporting evidence, validation, and tradeoffs in the template's collapsed details. Mermaid color meanings are author-defined; do not imply that the legend styles diagrams automatically.

Write content as bullets: one idea per `<li>`, usually 3–7 items per group. Keep paragraphs to one or two concise sentences; use tables for repeated comparisons and tests.

Done when the HTML has all eight sections, valid navigation and IDs, four rendered diagrams, escaped content, and no unresolved tokens.

## Prove

- Propose focused interface tests asserting results or collaborator effects; retain integration tests for ordering, persistence, and teardown.
- Cover meaningful success, failure, timeout, rejection, skip, and cancellation paths. Distinguish proposed checks from executed checks.
- Implement only when authorized. Commit, push, or open a PR only when requested.
- Preview the HTML when possible; inspect overflow, diagrams, and readability. Report preview limits honestly.

Deliver the HTML link, a short recommendation, and validation status. Do not duplicate the report in chat.
