# Content-selected visualization

Every visualization has `type`. Choose what answers the refactor question; none is valid. Before and after are current and proposed respectively. All labels/code are plain text; no custom markup or CSS is authored.

| Type | Use when | Fields |
| --- | --- | --- |
| `none` | A simple description already makes the change clear | Only `type` |
| `flow` | Data/control movement or responsibility transfer matters | `type`, `before`, `after`; each side a nonempty array of short step labels |
| `class` | State ownership, class boundaries or interfaces matter | `type`, `before`, `after`; each side has `classes`, `relations` |
| `sequence` | Ordering, calls or cleanup across participants matters | `type`, `before`, `after`; each side has `participants`, `messages` |
| `code` | A small local extraction is clearest in code | `type`, `language`, `before`, `after`; code strings |

Class side: nonempty `classes` array of `{ "name": "Owner", "members": ["operation()"] }`; names unique, members may be empty. `relations` array (may be empty) of `{ "from": "Owner", "to": "Policy", "label": "owns" }`; both names must exist on that side. Include only meaningful members and relations. Show existing/proposed owners, not a speculative hierarchy.

Sequence side: unique nonempty `participants` array of names; nonempty `messages` array of `{ "from": "Endpoint", "to": "Processor", "label": "close()" }`; participants must exist. Array order is event order. Use 2–4 participants when possible. Label conditions directly (e.g. "on disconnect: export"); keep branches, concurrency and failure detail in textual constraints rather than implying a misleading total order.

Code uses faithful inspected `before` excerpts and explicitly proposed `after` excerpts; cite sources in evidence. Use flow/class/sequence only when they add understanding. All types are generated with HTML/CSS, including class boxes and sequence lanes; no SVG/browser runtime is needed.
