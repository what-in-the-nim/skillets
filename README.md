# Skillets

Personal, reusable skills for agentic coding.

## Skills

- [`code-principles`](skills/code-principles/SKILL.md) — surgical coding defaults for formatting, documentation, composition, comments, and scope.
- [`testing-principle`](skills/testing-principle/SKILL.md) — pytest guidance for realistic collaborators, test organization, fixtures, parametrization, and assertions.

These are the canonical package names for the coding-principles and test-principles skills.

## Install

Clone the repository, then symlink the skills into an agent's personal skill directory:

```sh
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/code-principles" ~/.agents/skills/code-principles
ln -s "$PWD/skills/testing-principle" ~/.agents/skills/testing-principle
```

Replace `$PWD` with the clone's absolute path when running the commands from another directory. Existing installations at those destinations must be moved or removed first.
