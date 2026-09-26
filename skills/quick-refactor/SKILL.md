---
name: quick-refactor
description: Use Sol to find three evidence-backed refactor choices and recommend one, then Luna to produce an HTML report. Use when the user asks for a quick refactor opportunity or proposal.
---

# Quick Refactor

Present three distinct refactor choices when the code supports them, then recommend one. Keep the proposal behavior-preserving and identify the recommended choice's smallest useful first PR. If fewer than three are supported, explain why and leave the list shorter.

## Route the work

- Sol owns Find and Design; Luna owns Show and HTML generation. Use the available Sol and Luna model identifiers, defaulting to `gpt-6-sol` with high effort and `gpt-6-luna` with medium effort. Follow an explicit user model override.
- When the current agent is Sol, do Find and Design directly. Otherwise dispatch one Sol worker with fresh context (`fork_turns="none"` where supported): pass the target, absolute repository and skill paths, user constraints, and a fresh output directory. Give it only Find, Design, and the handoff requirements below. The coordinator handles dispatch and delivery without repeating the investigation.
- Reserve a fresh output directory beside relevant design documentation or at the requested location. Preserve existing artifacts unless replacement was explicitly requested. If model-selectable delegation is unavailable, disclose the limitation and complete the workflow on the current model; do not claim the requested split occurred.

## Find — 40%

- Read repository guidance and status; preserve unrelated work. Treat a user-named module as the starting scope.
- If no target is named, make a lightweight scan for distinct seams. If the user names a target, inspect it and its immediate neighbors. Seek three candidates grounded in concrete friction: split ownership, duplicated decisions, scattered state, or broad setup for a small behavior.
- Make the choices distinct responsibility seams, not variations of one design. For each, inspect its responsible code and one direct caller or relevant test; cite the source evidence, likely benefit, and a small first slice. Expand one hop only when needed to settle ownership or a contract. Trace lifecycle, ordering, failure, or cancellation only when relevant.
- Stop after three supported candidates. Do not pad the choices: if the bounded scan supports fewer than three, say why. Run a focused test or probe only to resolve a concrete uncertainty.

## Design — 40%

- Present the choices in a short comparison: source-grounded friction, expected benefit, first slice, and main tradeoff for each.
- Recommend one choice and give it the fuller design: responsibility, destination owner, narrow interface, reduced coupling/decisions/state/setup, and the invariant that remains intact. Keep the other choices concise.
- Define the recommended first PR by affected files, caller changes, preserved behavior, and focused acceptance checks. Separate deferred parts of the target design when they matter.
- Prefer an existing owner; add a class when state, invariants, or lifecycle need one. Use a function for stateless work. Keep policy with its domain owner.
- State tradeoffs that help distinguish the three choices. Keep bug fixes and behavior changes separate from the refactors.

## Show — 20%

Sol finishes by writing `handoff.md`, using [the example](examples/proposal.md). Include target, revision, date, source locations and evidence strengths for each choice, benefits/tradeoffs/first slices, the recommendation and its reason, owner and interface, preserved invariants, affected files, deferred work, and executed versus proposed checks. Describe the before/after flow as nodes and edges or fenced Mermaid. Keep it concise: up to three bullets per section.

The handoff is complete when Luna can produce the report without inspecting application code or choosing the design. Sol supplies any lifecycle or ordering constraints the diagram must preserve. Send incomplete or ambiguous technical details back to Sol before rendering.

Dispatch one Luna worker with fresh context: pass only the absolute handoff path, output directory, skill path, and [render-worker instructions](render-worker.md). Wait for its result. After Luna's fidelity preflight, give Sol only `proposal.json`, the authored `.mmd` files, and the render/check summary for comparison with its existing handoff. Sol checks recommendation, source references and confidence qualifiers, invariants, diagram semantics, and first-PR scope. Keep generated HTML, CSS, and SVG out of Sol's review context; Luna owns artifact and presentation checks. Reuse the same workers for corrections rather than restarting their investigation.

## Deliver

Deliver `report.html`, with `handoff.md` and renderer inputs retained beside it for review and regeneration. Headless browser compilation by the existing renderer is allowed; open a visible browser preview only when requested. If rendering is blocked, deliver the handoff and the exact rendering limitation.

Give the HTML link, a short recommendation, and which checks ran. Record actual worker models/efforts and available per-agent input, cached input, output, tool calls, and elapsed time in the improvement ledger when evaluating a run. Treat savings as unverified until usage and applicable model/cache prices support them.

Implement only when authorized; commit, push, or open a PR only when requested.
