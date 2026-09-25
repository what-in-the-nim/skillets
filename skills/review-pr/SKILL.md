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
  - Run `python3 <skill-dir>/scripts/review_pr.py lookup --number N --output /tmp/pr-N.json`.
    Use `--remote NAME` when the target repository is not `origin`.
  - The command derives the Gitea owner/repository from that remote, rejects API errors,
    saves the raw response, and prints compact PR metadata including the author.
- **Pin the refs**
  - For PRs, use remote-tracking refs such as `--source origin/feature/login --target origin/dev`.
    Add a fork remote when the head is in a fork. Bare branch names are for branch reviews.
- **Prepare the bundle**
  - Run `python3 <skill-dir>/scripts/review_pr.py prepare --source REF [--target REF]`.
    Add `--expected-head SHA --repo-url URL` for a PR.
  - The script fetches remote-tracking refs, defaults to `origin/dev`, verifies the head,
    and prints only a temporary bundle path.
  - `prepare` and `preflight` write Git fetch metadata. If the sandbox denies
    `.git/FETCH_HEAD`, retry the same command with repository metadata access.
- **Collect PR evidence**
  - Copy the lookup response into the bundle as `pr.json`, then run
    `python3 <skill-dir>/scripts/review_pr.py collect --bundle DIR --number N`.
  - The command saves all pages of Gitea's files, reviews, issue comments,
    per-review inline comments, and full diff. It reports counts without printing
    bulk responses. If inline retrieval fails or disagrees with PR metadata,
    investigate the PR page and record the history limit in the review.
- **Check intake**
  - After collection succeeds, run `python3 <skill-dir>/scripts/review_pr.py intake --bundle DIR`.
  - Its compact output checks PR refs and reconciles every changed file with `manifest.json`.
    Read `files.txt`. If inline comments are unavailable, state the resulting history
    limit in the review.
- **Choose the reviewer**
  - Review a contained patch directly. For a broad or cross-module change, delegate
    the technical review to one subagent; pass bundle and repository paths, not copied
    diff text or the full lead history.
  - The reviewer reads Gitea's diff for a PR or `diff.patch` for a branch, every changed
    file at the recorded source SHA (target SHA for deletions), and listed docs.

## Review

- **Technical owner:** The lead when reviewing alone, otherwise the reviewer. Trace
  callers, removed behavior, failure paths, and documented contracts. Return coverage
  for every changed file, including tests, config, and migrations, plus candidate findings
  with the code path and consequence. Run a focused reproduction or test when a finding
  needs one; broaden tests only for a concrete remaining risk.
- **Lead with reviewer:** Check coverage against `files.txt` and the decisive evidence for
  each finding. Send gaps back as targeted follow-ups; avoid repeating the full code trace.
  Own prior-finding reconciliation, the verdict, and publication. Discard unsupported claims.
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

- **Choose the verdict:** For a PR, use `REQUEST_CHANGES`, `APPROVED`, or `COMMENT`
  as the Gitea API event.
  Run `tea whoami` and compare its login with the author from `lookup`. For your own PR,
  use `COMMENT`; align the body heading with that verdict.
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
  - When using the Gitea reviews API, create the review with `body`, `commit_id`, and the
    selected event. Inspect the returned `state`: if it is `PENDING`, submit that review ID
    through `POST repos/OWNER/REPO/pulls/N/reviews/ID` with the same body and event.
  - Read back the final verdict, reviewed commit, exact body, and permalink URLs.
    A `PENDING` review is unfinished.
  - Check the Gitea page before claiming the links render as previews.
- **Report:** Give the local file, PR URL, and result. A branch without a PR produces
  only the local review.
