---
name: quick-refactor
description: Find three evidence-backed refactor choices with Sol, let the user select, then deepen that choice in a static HTML report. Use when the user asks for a quick refactor opportunity or proposal.
---

# Quick Refactor

Default to two stages: **compare → user selects → deepen**. Recommend a choice without treating that recommendation as selection. If the user explicitly says “choose for me” or already specifies a choice to deepen, proceed with that selection.

## Route and preserve

Sol owns investigation and design (`gpt-6-sol`, high); Luna coordinates and generates HTML (`gpt-6-luna`, medium). Follow explicit model overrides. When the current agent is Sol, author directly; otherwise dispatch one fresh Sol with target, absolute repository/skill paths, constraints, fresh output directory and the current stage only. Disclose unavailable model-selectable delegation.

The coordinator runs the Python renderer directly. Retain the Sol worker ID, artifact path and inspected revision for continuation. Reuse that worker for corrections and selected design; if unavailable, give a fresh Sol the selected choice, prior artifact, evidence and constraints. Preserve existing artifacts and unrelated WIP. Store the choices report and selected design in separate fresh directories.

## Stage 1 — Compare

1. Read repository guidance/status. Inventory paths with `rg --files`, search symbols, then batch bounded excerpts. Whole-file reads need a concrete ownership/ordering question. Inspect the named target and immediate neighbors; otherwise make a lightweight seam scan.
2. Seek three distinct seams: split ownership, duplicated decisions, scattered state or broad setup. For each inspect responsible code and one direct caller or relevant test. Record friction, benefit, confidence, small first slice and main tradeoff. Expand one hop only to settle support. Stop when three choices are supported; explain a shorter list. Keep detailed interfaces, lifecycle redesign and acceptance planning for stage 2.
3. Sol writes `proposal.json` with `stage: "choices"` using [the concise contract](authoring.md). Choose the appropriate visualization for each candidate; use none when a diagram would add no insight. Recommend one with a short reason. The coordinator generates the report using [render instructions](render-worker.md).
4. Deliver the report and ask the user to select by number/name/ID, or say “choose for me.” End the turn. Start stage 2 only after an explicit selection or existing delegation of that choice; elapsed time is not selection. The static report tells the reader to reply in chat and does not imply that clicking a card launches work.

## Stage 2 — Deepen selected choice

Confirm the selected ID and current repository HEAD/status. If source changed, refresh relevant excerpts and reassess that choice before designing; retain the earlier snapshot. Reuse existing evidence rather than repeating the whole scan.

Give Sol only the selected design task. Develop owner, responsibility boundary, narrow interface, preserved invariants, detailed visualization/code where useful, first-PR files/acceptance and deferred work. Prefer existing owners; functions for stateless work, classes for justified state/invariants/lifecycle. Separate bug fixes and behavior changes. Run tests/probes only when authorized and needed to settle a concrete uncertainty.

Author a new JSON with `stage: "design"` and `selected_choice`, using [selected-design fields](design.md). Retain the supported comparison and distinguish the user's choice from Sol's original recommendation. The coordinator renders deterministically. Return missing/ambiguous technical facts to the same Sol; routine second review of copied facts is unnecessary. Sol owns source support and semantics.

## Presentation and delivery

Visualization follows the content: flow for responsibilities/data movement, class for ownership/interfaces, sequence for ordering across participants, code comparison for a local extraction, none for an already clear change. Plain HTML/CSS generation uses no SVG, Mermaid, JavaScript or browser. The user opens the report. Keep all sections visible; use headings and spacing to keep the main path easy to scan. Visual readability remains unchecked unless inspection was requested.

Normal final response: report link, one-sentence recommendation, checks and next action, normally within 120 words. Stage 1 ends with the selection request; stage 2 gives the selected first PR. Keep detailed comparisons/design/evidence in HTML. On failure link retained JSON and state the exact limitation. Requested evaluation metrics or material limitations can extend the short format.

Keep read/retry/status/usage audit separate from technical input. When evaluating, use each agent's own usage records; account quota is not task usage. Record stage scopes separately and combined when complete. Savings need comparable quality and pricing. Implement, commit, push or open a PR only when authorized.
