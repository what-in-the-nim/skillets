---
name: quick-refactor
description: Find one high-value behavior-preserving refactor, bound its first change, and explain the improvement with a before/after diagram in a concise Markdown proposal. Use when the user asks for a quick refactor opportunity or proposal.
---

# Quick Refactor

Propose one refactor that reduces concrete complexity while preserving behavior and public contracts. Identify the smallest useful first PR. Say when no strong candidate emerges.

## Find — 40%

- Read repository guidance and status; preserve unrelated work. Treat a user-named module as the starting scope.
- If no target is named, make a lightweight scan and shortlist at most three candidates. Prefer concrete friction: split ownership, duplicated decisions, scattered state, or tests that require broad setup for a small behavior.
- Choose one candidate. Inspect its responsible code, direct callers, and relevant tests. Expand one hop only when needed to settle ownership or a contract. Trace lifecycle, ordering, failure, or cancellation only when the candidate depends on it.
- Stop when source evidence establishes the current owner, the specific friction, the invariant to preserve, and the first-PR boundary. Run a focused test or probe only to resolve a concrete uncertainty.

## Design — 40%

- State what responsibility moves, its destination owner and narrow interface, and how this reduces coupling, decisions, state, or test setup.
- Define the first PR by affected files, caller changes, preserved behavior, and focused acceptance checks. Separate deferred parts of the target design when they matter.
- Prefer an existing owner; add a class when state, invariants, or lifecycle need one. Use a function for stateless work. Keep policy with its domain owner.
- Compare one alternative only when it has a real tradeoff. Keep bug fixes and behavior changes separate from the refactor.

## Show — 20%

- Make one paired before/after flowchart the primary visual. Show the responsibility or decision moving, the simpler handoff, and the behavior or invariant that stays intact.
- Add a second diagram only when it answers a separate important question, such as a lifecycle or ordering risk. Avoid diagrams that only document every class or call.
- Label evidence as **reproduced behavior**, **source-supported risk**, or **proposed improvement**. Cite source locations or the command and result; distinguish executed checks from proposed checks.
- Keep the proposal concise: up to three bullets per section. Include the recommendation, primary diagram pair, target design, evidence/validation, and first PR.

## Deliver

Start from [the Markdown example](examples/proposal.md). Save one Markdown proposal at the user-requested path or beside the relevant design documentation. Embed diagrams as fenced `mermaid` blocks in that file; do not create separate JSON or diagram-source files.

Keep all rendering in the viewing platform. The skill must not launch a browser, call the HTML renderer, or preview the report in a browser.

Implement only when authorized; commit, push, or open a PR only when requested. Deliver the Markdown link, a short recommendation, and whether checks were executed, without duplicating the report in chat.
