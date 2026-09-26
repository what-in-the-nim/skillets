# Selected-design fields

Continue from the choice-report contract with `stage: "design"`. Add `selected_choice` (existing ID), `design`, and `first_pr`. The selection can differ from `recommended_choice`; retain that distinction. Preserve the comparison snapshot and update evidence/revision when relevant source changed.

`design`: required `owner`, `boundary` (text); nonempty text arrays `interface`, `invariants`; text array `lifecycle` (may be empty); `visualization` from the visualization contract. Optional `code`: `language`, `before`, `after` (nonempty text).

`first_pr`: `summary` (one sentence); nonempty text arrays `files`, `acceptance`; text array `deferred` (may be empty).

Deepen only the selected seam. Choose the visualization that explains its hardest question; use a larger class/sequence view when needed, or none. Keep the main diagram short and put detailed conditional paths in lifecycle. Preserve every important invariant in the visible supporting detail.

Code comparisons use faithfully copied current source and explicitly proposed after excerpts. Cite the current excerpt in evidence. Prefer 5–12 lines per side, using `...` for omitted context. The renderer displays escaped `<pre><code>` blocks. Code snippets are explanatory excerpts, not implementation or proof of behavior preservation.
