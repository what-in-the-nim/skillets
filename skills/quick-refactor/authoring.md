# Choice-report contract (version 3)

Sol authors plain-text JSON; the renderer escapes it. Objects use exactly the required fields. Default stage is a comparison, not a completed redesign.

| Field | Content |
| --- | --- |
| `schema_version`, `stage` | Integer `3`; `"choices"` |
| `title`, `target`, `repository`, `revision`, `date` | Nonempty text; absolute repository and full inspected HEAD |
| `evidence_status` | Short actual inspection/test status |
| `choices` | 1–3 objects with unique slug `id`, `title`, `friction`, `benefit`, `first_slice`, `tradeoff`, nonempty `evidence_ids`, `visualization` |
| `shorter_list_reason` | Empty for three; explanation required for fewer |
| `recommended_choice`, `recommendation_reason` | Existing choice ID and one-sentence reason; not a user selection |
| `evidence` | Objects: unique slug `id`, matching `choice_id`, `strength`, `confidence`, `claim`, `sources` |
| `sources` | Objects: repository-relative `path`, integer `line`, inclusive `end_line` |
| `checks` | Objects: `status` (`executed`, `proposed`, `not run`), `description`, `result` |

Each choice links to its own evidence; every evidence entry belongs to a choice. Real reports require nonempty sources. `strength`: `reproduced behavior`, `source-supported risk`, `proposed improvement`. Keep finer confidence in `confidence`; inspection is not reproduction.

Use short action-oriented titles and short sentences in cards. A first slice is a scope estimate, not detailed acceptance planning. Include essential risks that could affect selection; defer detailed design. Stage 1 contains no `design`, `first_pr` or `selected_choice` fields.

Choose each card's [visualization](visualizations.md) according to the seam; types can differ among choices. Prefer 2–3 nodes/classes/messages per side in this stage. Use `{"type":"none"}` when words or code already explain the change. Keep comparable before/after operations and accurate ownership; avoid inventing classes to get a diagram.

After selection, add only the [selected-design fields](design.md). Load [the complete example](examples/proposal.json) only if the contract or a diagnostic leaves the shape unclear. The coordinator follows [render instructions](render-worker.md).
