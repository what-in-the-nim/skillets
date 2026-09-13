# Offline report renderer

Run `python3 /absolute/path/to/quick-refactor/scripts/render_proposal.py proposal.json -o report.html` from any directory. Requires Python 3.10+ on macOS/Linux and an installed Chrome/Chromium. Set `CHROME_PATH` or pass `--browser /path/to/executable` if automatic discovery fails. The renderer uses an isolated temporary browser profile, bundled Mermaid 11.12.0, blocked network resolution, and a restrictive content policy. It never installs packages or downloads a browser. A browser must be allowed to launch in the execution environment; failures leave the previous report intact.

The output is static HTML with embedded SVGs: viewing needs neither JavaScript nor a network connection. Source files remain authoritative: edit JSON or `.mmd`, including follow-up additions, then run the same command. Direct edits to generated HTML are overwritten.

## Content format

Copy [the runnable example](../examples/proposal.json) and its `.mmd` files. This structured schema replaces the old fixed uppercase-token JSON format; migrate old content into section `body_html` and diagram pairs.

Top-level required fields: `title`, `target`, `revision`, `date` (nonempty text), and `sections` (ordered array). Unknown keys are errors.

Every section has a unique slug `id` and plain-text `title`. At least one content field must be populated:

| Field | Meaning |
| --- | --- |
| `body_html` | Trusted static HTML fragment: bullets, tables, code, links, or a legend for colors actually used. Do not include active content or external assets. |
| `diagrams` | Object with `before` and `after`, each an `@relative/path.mmd` reference resolved beside the JSON. Each pair compiles before publication. |
| `evidence` | Array of objects with `strength`, `text`, and `source` (plain text). |
| `collapsed` | Optional boolean for supporting sections; defaults to false. |

Required IDs: `recommendation`, `process`, `target-design`, `evidence`, `validation`, `first-pr`. Lead with `recommendation`, then `process`; the latter requires paired flowcharts. Keep `recommendation`, `process`, `target-design`, and `first-pr` expanded. The evidence section requires labeled entries. Add optional sections anywhere after the first two: for example ownership diagrams, sequence diagrams, comparisons, and tradeoffs. Navigation and section numbering follow array order.

Evidence strengths:

- `reproduced behavior`: observed via an executed test or probe; cite the command/result and relevant source location.
- `source-supported risk`: a plausible failure supported by source paths and conditions, without claiming reproduction.
- `proposed improvement`: design benefit or illustrative example that has not established a runtime defect.

Describe the complete requested design in `target-design`; bound files, tests, acceptance criteria, and deferred work in `first-pr`. After diagrams show the target design.

## Checks and maintenance

One render validates required content, unknown fields, diagram compilation, navigation, document-wide ID uniqueness, SVG/ARIA references, and unresolved `{{tokens}}`. SVG IDs and their references are namespaced per diagram, including sequence markers. Rendering errors fail closed; nothing replaces the previous report. Automated checks do not establish source evidence or visual readability: inspect the output when possible and report preview limits.

Run the focused regression check with `python3 scripts/test_renderer.py` from the skill directory. It compiles all three example diagram types offline, verifies follow-up edits and optional-section removal, and checks that bad diagrams and broken navigation preserve an existing artifact.

The vendored Mermaid file and its MIT license are in `../vendor`; provenance and checksum are recorded there. To upgrade, intentionally replace the pinned distribution and update that record, then run the regression check. Browser layout can vary across browser/OS versions; reproducibility here means all authored content survives rerendering, not byte-identical HTML across machines.

API references: [Mermaid rendering](https://mermaid.js.org/config/usage.html) and [deterministic IDs](https://mermaid.js.org/config/schema-docs/config).
