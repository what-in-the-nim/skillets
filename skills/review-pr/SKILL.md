---
name: review-pr
description: Review a Gitea PR or branch, track findings across re-reviews, and submit a PR review when authorized.
disable-model-invocation: true
---

# Review PR

Run from the target repository. Use `gitea` for PR lookup, discussion, submission, and readback.

- `review-pr 123`: review PR 123.
- `review-pr feature/login`: review the branch against `origin/dev`.
- `review-pr feature/login against main`: review against `main`.

## Prepare

- **Read the PR**
  - Save the raw Gitea PR API response to a temporary file.
  - Print only its title, head SHA, base, and repository URL.
- **Pin the refs**
  - Fetch the exact head and base as remote-tracking refs, including a fork remote when needed.
  - For PRs, pass qualified refs such as `--source origin/feature/login --target origin/dev`.
    Bare branch names are for branch reviews.
- **Prepare the bundle**
  - Run `python3 <skill-dir>/scripts/review_pr.py prepare --source REF [--target REF]`.
    Add `--expected-head SHA --repo-url URL` for a PR.
  - The script refreshes remote-tracking refs, defaults to `origin/dev`, verifies the head,
    and prints only a temporary bundle path.
- **Save PR evidence**
  - Move the saved PR response into the bundle as `pr.json`.
  - Save Gitea's files, reviews, issue comments, inline comments, and full diff as
    `gitea-files.json`, `reviews.json`, `discussion.json`, `inline.json`, and `gitea.diff`.
  - Combine all pages of each paginated list into its JSON file. Keep bulk responses
    out of the model output.
- **Check intake**
  - Run `python3 <skill-dir>/scripts/review_pr.py intake --bundle DIR`.
  - Its compact output checks PR refs and reconciles every changed file with `manifest.json`.
    Read `files.txt`.
- **Hand off**
  - Pass bundle and repository paths, rather than copied diff text, to one reviewer subagent.
  - It reads Gitea's diff for a PR or `diff.patch` for a branch, every changed file at the
    recorded source SHA (target SHA for deletions), and listed docs.

## Review

- **Reviewer:** Trace callers, removed behavior, failure paths, and documented contracts.
  Return candidate findings and coverage for every changed file, including tests, config,
  and migrations.
- **Lead:** Check coverage against `files.txt` and send omissions back. Own prior-finding
  reconciliation, focused reproductions, the verdict, and publication. Run relevant tests
  when feasible. Independently verify each finding against current code and a concrete
  consequence; discard unsupported claims.
- **Severity:** List findings in order: 🔴 Blocker, 🟠 Medium risk, 🟡 Low risk, 🔵 Nit.
  Use the same labels in the local file and published body.
- **Re-review status:** Match prior findings by problem. Use the exact labels `🆕 NEW`,
  `🔁 STILL_OPEN`, and `✅ FIXED`, with evidence in both the local review and published body.
- **Local review:** Write `manifest.json`'s `review_file` with:
  - The title, reviewed SHA/date, and a summary of tests and limits.
  - `## Findings` with `path:line`, severity, consequence, and fix (or `No findings.`).
  - One current `## Out of scope / notes`.
- **Re-review history:** Replace current findings and prepend a `## Changes since last review`
  table of status transitions. Keep older change sections.

## Publish

- **Choose the verdict:** For a PR, use `REQUEST_CHANGES`, `APPROVE`, or `COMMENT`.
  Draft the body using [the request-changes template](templates/request-changes.md) when appropriate.
- **Add code links**
  - Put `{{code:path:L10-L15}}` on its own line after each current-code finding, or
    `{{base-code:path:L10-L15}}` for removed code.
  - Run `python3 <skill-dir>/scripts/review_pr.py format --bundle DIR --draft FILE`.
    It validates ranges and writes bare Gitea commit permalinks to `body.md` for code previews.
  - Review the resulting body and test evidence.
- **Show the review:** Show the complete review to the user.
- **Check refs:** Re-read the PR head and base through `gitea`, then run
  `python3 <skill-dir>/scripts/review_pr.py preflight --bundle DIR --current-pr-head SHA --current-pr-base BRANCH`.
  If refs changed, review again.
- **Submit and verify**
  - Submit one review through `gitea` within existing authorization; otherwise present
    the complete draft for approval.
  - Read back the verdict, reviewed commit, exact body, and permalink URLs.
  - Check the Gitea page before claiming the links render as previews.
- **Report:** Give the local file, PR URL, and result. A branch without a PR produces
  only the local review.
