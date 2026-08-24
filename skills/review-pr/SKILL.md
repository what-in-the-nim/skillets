---
name: review-pr
description: >-
  Review a Gitea pull request with tea and post one review. Takes the PR number.
allowed-tools: Bash, Read, Grep, Glob
disable-model-invocation: true
---

# Review PR (Gitea)

Review a Gitea pull request and post the review back to the PR. The input is a single PR
number (e.g. `743`).

## Gitea connection

Apply the model-invoked `gitea` skill for every Gitea operation in this workflow. It is
the source of truth for repository and login discovery, target disambiguation, tea
command selection, authentication errors, and mutation verification.

## Workflow

Run these in order. Do not skip the codebase search step — it is what separates a real
review from a diff-only skim.

### 1. Fetch PR metadata + diff

```bash
N=743
tea pulls "$N" --fields index,title,state,author,url,body,mergeable,base,head --output yaml
tea pulls "$N" --fields diff --output simple
```
Read the body and full diff. Build the changed-file list from the unified diff headers,
then verify the diff delivers the stated intent.

### 2. Ground the review in the codebase

A diff lies by omission. Before forming conclusions, check the surrounding code:

- **Consumers:** `rg` for callers of any new/changed public method. A new API with no
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
BODY_FILE=/tmp/review.md
tea pulls reject "$N" "$(cat "$BODY_FILE")"   # REQUEST_CHANGES
tea pulls approve "$N" "$(cat "$BODY_FILE")"  # APPROVE
tea pulls review "$N"                           # COMMENT: select Comment and paste the body
```
Write the review body to a Markdown file under a scratch directory. Run exactly one of
the three commands. Relay the verdict and PR URL from step 1 to the user.

## Notes

- Keep the whole review as one review submission, not many inline comments, unless the
  user asks for inline line comments.
- If a `tea` operation fails, return to the `gitea` skill's target-resolution and
  authentication guidance before retrying with an explicit target.
