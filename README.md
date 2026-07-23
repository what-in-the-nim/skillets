# Skillets

Personal, reusable skills for agentic coding.

## Skills

- [`code-principle`](skills/code-principle/SKILL.md) — surgical coding defaults for formatting, documentation, composition, comments, and scope.
- [`testing-principle`](skills/testing-principle/SKILL.md) — pytest guidance for realistic collaborators, test organization, fixtures, parametrization, and assertions.

These are the canonical package names for the coding-principle and test-principle skills.

## Install

### With `npx skills`

Install both skills globally for Codex:

```sh
npx skills add what-in-the-nim/skillets -g --agent codex --skill code-principle --skill testing-principle --yes
```

Use `--list` to inspect the available skills before installing, or omit `-g` to install them only in the current project.

### From a local clone

Clone the repository, then symlink the skills into an agent's personal skill directory:

```sh
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/code-principle" ~/.agents/skills/code-principle
ln -s "$PWD/skills/testing-principle" ~/.agents/skills/testing-principle
```

Replace `$PWD` with the clone's absolute path when running the commands from another directory. Existing installations at those destinations must be moved or removed first.
