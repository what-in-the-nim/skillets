---
name: code-principle
description: Apply surgical coding defaults when writing, modifying, or refactoring code.
---

# Code Principle

Apply all six rules to code you create or modify:

1. **Formatting.** Preserve manual formatting. Run required non-mutating checks; format files only when explicitly requested.
2. **Docstrings.** Document every new module, class, function, and method. Start with a one-line summary; expand into relevant NumPy-style sections for contracts, side effects, errors, or non-obvious decisions.
3. **Composition.** Before implementing a module or class, identify separable mechanisms with independent responsibilities, contracts, or testing value. Compose reusable components where justified; keep speculative extractions local.
4. **Comments.** Allow at most two inline comments per function or method: one line each, explaining why. Put deeper explanation in docstrings or a nearby `README.md`.
5. **Surgical scope.** Start with the smallest correct patch fitting the current design. Refactor only as the required change grows, and only enough to keep it coherent. For refactors, preserve intended caller-visible contracts, including validation, initialization, and synchronization boundaries. Before widening scope for an apparent regression, compare old and new reachable caller paths.
6. **Terse communication.** Use compact engineering prose; fragments are fine when unambiguous. Preserve decisions, risks, and verification evidence.

Before finishing, verify the diff and handoff against all six rules.

## Repeated mechanical work

When a task repeats asset preparation, validation setup, evidence collection, or result formatting, inspect project guidance and existing commands first. Reuse an existing helper or task runner. Extract a small deterministic script when observed repetition justifies it; keep test selection, diagnosis, design, and review judgment with the agent.

Follow the repository's layout. Otherwise use `scripts/` for developer and CI tooling, `.agents/scripts/` for agent-specific tooling, and a skill's `scripts/` for reusable skill mechanics. In the nearest applicable `AGENTS.md`, add a concise pointer with the invocation, triggering condition, and output location. Keep detailed contracts in `--help` or a nearby README.

Helpers accept explicit paths and options, preserve failure exit codes, save full evidence to files, and print compact summaries with artifact paths. For temporary asset changes, verify content against the expected hash, record originals in a recovery manifest, and restore them on exit; make interrupted-run restoration explicit. Use existing process-session tools to await long commands rather than repeatedly printing log tails.
