# Skillets

Personal, reusable skills for agentic coding.

## Skills

- [`code-principle`](skills/code-principle/SKILL.md) — surgical coding defaults for formatting, documentation, composition, comments, and scope.
- [`code-guide`](skills/code-guide/SKILL.md) — iterative, source-grounded explanations of code, diffs, PR changes, classes, modules, and packages.
- [`code-qa`](skills/code-qa/SKILL.md) — concise, source-grounded guidance through code created or changed in the current task.
- [`class-design`](skills/class-design/SKILL.md) — principles for cohesive, minimal, invariant-preserving, and lifecycle-safe classes.
- [`testing-principle`](skills/testing-principle/SKILL.md) — pytest guidance for realistic collaborators, test organization, fixtures, parametrization, and assertions.
- [`pytest-skill`](skills/pytest-skill/SKILL.md) — pytest examples and reference material for fixtures, parametrization, markers, mocking, and configuration.
- [`gitea`](skills/gitea/SKILL.md) — model-invoked Gitea operations through the `tea` CLI.
- [`review-pr`](skills/review-pr/SKILL.md) — user-invoked Gitea PR or branch review with tracked re-reviews and a request-changes template. Invoke as `review-pr 123` for PR 123.
- [`quick-refactor`](skills/quick-refactor/SKILL.md) — small refactor proposals with HTML reports and Mermaid diagrams.

These are the canonical package names for the coding-principle, code-guide, code-qa, class-design, testing-principle, pytest, quick-refactor, Gitea, and Gitea PR-review skills.

## Install

### With `npx skills`

Install all skills globally for Codex:

```sh
npx skills add what-in-the-nim/skillets -g
```

Install one skill by naming it with `--skill`:

```sh
npx skills add what-in-the-nim/skillets --skill code-qa -g
```

Use `--list` to inspect the available skills before installing. Omit `-g` to install all skills or the selected skill only in the current project.

### From a local clone

Clone the repository, then run the installer from the clone root:

```sh
./scripts/install-local.sh
```

The script symlinks every skill into `~/.agents/skills`. Existing installations at those
destinations must be moved or removed first.
