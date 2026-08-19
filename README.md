# Skillets

Personal, reusable skills for agentic coding.

## Skills

- [`code-principle`](skills/code-principle/SKILL.md) — surgical coding defaults for formatting, documentation, composition, comments, and scope.
- [`code-guide`](skills/code-guide/SKILL.md) — concise, source-grounded guidance through code created or changed in the current task.
- [`lifecycle-design`](skills/lifecycle-design/SKILL.md) — lifecycle guidance for state, invariants, ownership, cleanup, concurrency, failure, and API design.
- [`testing-principle`](skills/testing-principle/SKILL.md) — pytest guidance for realistic collaborators, test organization, fixtures, parametrization, and assertions.
- [`pytest-skill`](skills/pytest-skill/SKILL.md) — pytest examples and reference material for fixtures, parametrization, markers, mocking, and configuration.
- [`review-pr`](skills/review-pr/SKILL.md) — Gitea pull-request review workflow with a reusable API helper.

These are the canonical package names for the coding-principle, code-guide, lifecycle-design, test-principle, pytest, and Gitea PR-review skills.

## Install

### With `npx skills`

Install all skills globally for Codex:

```sh
npx skills add what-in-the-nim/skillets -g --agent codex --skill code-principle --skill code-guide --skill lifecycle-design --skill testing-principle --skill pytest-skill --skill review-pr --yes
```

Use `--list` to inspect the available skills before installing, or omit `-g` to install them only in the current project.

### From a local clone

Clone the repository, then symlink the skills into an agent's personal skill directory:

```sh
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/code-principle" ~/.agents/skills/code-principle
ln -s "$PWD/skills/code-guide" ~/.agents/skills/code-guide
ln -s "$PWD/skills/lifecycle-design" ~/.agents/skills/lifecycle-design
ln -s "$PWD/skills/testing-principle" ~/.agents/skills/testing-principle
ln -s "$PWD/skills/pytest-skill" ~/.agents/skills/pytest-skill
ln -s "$PWD/skills/review-pr" ~/.agents/skills/review-pr
```

Replace `$PWD` with the clone's absolute path when running the commands from another directory. Existing installations at those destinations must be moved or removed first.
