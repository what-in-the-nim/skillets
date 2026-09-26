# Static HTML report

Run `python3 /absolute/skill/path/scripts/render_proposal.py proposal.json --check-sources -o report.html`. Requires Python 3.10+ and Git for optional source checks. No packages, browser, scripts, SVG or network assets are used. Output is HTML/CSS that the reader opens themselves, plus derived `handoff.md`. Version 3 has separate choices and selected-design stages. Choice cards select flow, class, sequence, code or no visualization; selected designs retain visible invariants/evidence. Edit JSON and regenerate; generated files are not authoring inputs.

## Authoring

Sol uses [the concise choices contract](../authoring.md), then [selected-design fields](../design.md) only after selection. Consult [the complete example](../examples/proposal.json) only when the field/type contract or a validation diagnostic is insufficient.

## Validation and limits

The command validates the entire structure and references before writing. With `--check-sources`, it requires evidence source references, checks HEAD against `revision`, and verifies paths/ranges. It escapes all authored text and maps every technical field to a fixed place in the report. It produces a compact summary instead of dumping HTML. `--validate-only` performs these checks without writing.

Individual artifacts are replaced atomically after validation; publication of HTML and Markdown is not a multi-file transaction. Existing non-generated handoffs cause failure; use a fresh directory. These checks establish structural completeness and preservation, not source support, behavioral equivalence, source freshness within a dirty checkout, or visual readability. Sol owns those technical judgments. Version-2 structured design inputs remain supported. Legacy `sections`/`body_html`/Mermaid inputs require explicit migration and remain untouched. Version-3 choices inputs reject design/first-PR/selection fields; design inputs require a valid selected ID. The renderer verifies visualization references, not whether the selected diagram captures all relevant behavior.
