# Skillets

Personal, reusable skills for agentic coding.

## Skills

- [`code-principle`](skills/code-principle/SKILL.md) — surgical coding defaults for formatting, documentation, composition, comments, and scope.
- [`code-guide`](skills/code-guide/SKILL.md) — concise, source-grounded guidance through code created or changed in the current task.
- [`lifecycle-design`](skills/lifecycle-design/SKILL.md) — lifecycle guidance for state, invariants, ownership, cleanup, concurrency, failure, and API design.
- [`testing-principle`](skills/testing-principle/SKILL.md) — pytest guidance for realistic collaborators, test organization, fixtures, parametrization, and assertions.
- [`pytest-skill`](skills/pytest-skill/SKILL.md) — pytest examples and reference material for fixtures, parametrization, markers, mocking, and configuration.
- [`gitea`](skills/gitea/SKILL.md) — model-invoked Gitea operations through the `tea` CLI.
- [`review-pr`](skills/review-pr/SKILL.md) — Gitea pull-request review workflow using the `tea` CLI.

These are the canonical package names for the coding-principle, code-guide, lifecycle-design, testing-principle, pytest, Gitea, and Gitea PR-review skills.

## Install

### With `npx skills`

Install all skills globally for Codex:

```sh
npx skills add what-in-the-nim/skillets -g
```

Use `--list` to inspect the available skills before installing, or omit `-g` to install them only in the current project.

### From a local clone

Clone the repository, then run the installer from the clone root:

```sh
./scripts/install-local.sh
```

The script symlinks every skill into `~/.agents/skills`. Existing installations at those
destinations must be moved or removed first.
