# Generate and deliver

The coordinator runs this step directly after Sol supplies `proposal.json`. Technical content comes from Sol; layout comes from the fixed template.

```sh
python3 /absolute/skill/path/scripts/render_proposal.py /absolute/output/path/proposal.json --check-sources -o /absolute/output/path/report.html
```

`--check-sources` verifies current HEAD, source paths and line ranges. It does not establish that a claim follows from the source. Omit it only for illustrative examples, and disclose unchecked source references. Use `--validate-only` to check without writing artifacts.

The renderer uses Python's standard library, escapes all authored text, validates the contract, and generates both HTML and a derived `handoff.md`. All layout is reusable. The JSON stage selects the choices report or selected redesign. Structured flow, class, sequence and code visuals use HTML/CSS; `none` emits no diagram. After a choices report, deliver it and wait for the user’s selection in chat. No browser, SVG or preview is needed.

On failure, retain the inputs and existing report. Send technical corrections to the same Sol worker; rerun the same command after the canonical JSON is corrected. Deliver the paths and compact check summary; keep generated HTML out of model output. State that visual readability was not inspected unless requested.
