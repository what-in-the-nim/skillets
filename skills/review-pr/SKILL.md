---
name: review-pr
description: >-
  Review a Gitea pull request by number and post the review back to Gitea. Use when the
  user asks to "review PR <N>", "review-pr <N>", "review pull request <N>", or to review
  and comment on a Gitea PR. Takes a single argument: the PR number. The skill fetches the
  PR metadata + diff from this repo's Gitea instance, reviews the change for correctness,
  SOLID design, surgical scope, and extensibility (not overfit), then posts a single
  REQUEST_CHANGES / APPROVE / COMMENT review to the PR.
allowed-tools: Bash, Read, Grep, Glob
---

# Review PR (Gitea)

Review a Gitea pull request and post the review back to the PR. The input is a single PR
number (e.g. `743`).

## Connection

This repo's Gitea instance and credentials come from the repo `.env` (`GITEA_URL`,
`GITEA_TOKEN`) and `~/.netrc`. The owner/repo come from the `origin` remote.

> Note: the `.env` `GITEA_TOKEN` is often scoped to public repos only and fails on this
> private repo with `"token scope is limited to public repos"`. The reliable path is
> **`curl -n`** (HTTP basic auth from `~/.netrc`), which the helper script uses by default.

The helper script `scripts/gitea_pr.sh` wraps every API call. Always prefer it over
hand-rolling curl.

## Workflow

Run these in order. Do not skip the codebase grep step — it is what separates a real
review from a diff-only skim.

### 1. Fetch PR metadata + diff
```bash
bash .claude/skills/review-pr/scripts/gitea_pr.sh meta <N>    # title, body, +/-, files, mergeable
bash .claude/skills/review-pr/scripts/gitea_pr.sh files <N>   # changed file list with +/-
bash .claude/skills/review-pr/scripts/gitea_pr.sh diff  <N>   # full unified diff
```
Read the diff in full. Read the PR body to understand the author's stated intent — then
verify the diff actually delivers it.

### 2. Ground the review in the codebase
A diff lies by omission. Before forming conclusions, check the surrounding code:
- **Consumers:** `grep` for callers of any new/changed public method. A new API with no
  production caller is speculative generality (YAGNI) — a headline finding, not a nit.
- **Removed code:** open what a removed helper did (cleanup, tracing, error handling) and
  confirm the replacement preserves it. Watch for dropped spans/metrics and lost cleanup
  that cause unbounded growth.
- **Error/cancel paths:** trace `finally`, `except`, and cancellation. Caching or
  finalizing on partial/failed/cancelled work is a common correctness bug.
- **Interface shape:** type-sniffing (`isinstance`, `inspect.isawaitable`) on a shared
  method name signals an LSP/OCP smell that fights "easy to extend."

### 3. Form the review
Optimize for the user's standing bar: **surgical, SOLID, easy to extend, not overfit.**
- Order findings by importance: 🔴 Blocking, 🟡 Should fix, 🟢 Minor/nits, then What's good.
- Reference concrete `file:line`. State the concrete consequence, not a style preference.
- Pick a verdict: `REQUEST_CHANGES`, `APPROVE`, or `COMMENT`.
- Always include a short "What's good" section — reviews that only criticize get ignored.

### 4. Show the user, then post
Present the review in chat first. Posting is outward-facing — confirm before posting
unless the user already said to post (e.g. invoked the skill with "and post it"). Then:
```bash
bash .claude/skills/review-pr/scripts/gitea_pr.sh review <N> <EVENT> <body-file.md>
# EVENT ∈ REQUEST_CHANGES | APPROVE | COMMENT
```
Write the review body to a markdown file (e.g. under the scratchpad dir) and pass its
path. The script prints the posted review's id, state, and URL — relay the URL to the user.

## Notes
- Keep the whole review as one review submission, not many inline comments, unless the
  user asks for inline line comments.
- If `meta` returns all-null fields, the token lacked scope and the script silently fell
  back wrong — re-run; the script uses `-n` basic auth which works for private repos.
