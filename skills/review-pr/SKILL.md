---
name: review-pr
description: Review a Gitea PR or branch, track findings across re-reviews, and submit a PR review when authorized.
disable-model-invocation: true
---

# Review PR

Invoke as `review-pr 123`, `review-pr feature/login` (against `origin/dev`), or `review-pr feature/login against main`. Work from the target repository. Use `gitea` for PR lookup, discussion, submission, and readback.

## Prepare

For a PR, use `gitea` to read its head SHA, base, and repository URL. Resolve its exact head ref and remote-tracking base. For a branch, use the named source and target. Run `python3 <skill-dir>/scripts/review_pr.py prepare --source REF [--target REF]`; add `--expected-head SHA --repo-url URL` for a PR. The script refreshes remote-tracking refs, defaults to `origin/dev`, verifies the head, and prints only a temporary bundle path.

Save the PR title/body, full diff, and discussion including inline comments to bundle files through `gitea`, without printing bulk output. Read `manifest.json` and `files.txt`; reconcile their file list with Gitea's PR files. Pass bundle and repository paths, not copied diff text, to one reviewer subagent. It reads Gitea's diff for a PR or `diff.patch` for a branch, every changed file at the recorded source SHA (target SHA for deletions), listed docs, and any prior review.

## Review

Have the subagent trace callers, removed behavior, failure paths, and documented contracts. Require a coverage list for every changed file, including tests, config, and migrations. Check it against `files.txt`; send omissions back. Run relevant tests when feasible. Verify each proposed finding against current code and a concrete consequence; discard unsupported claims. Label findings, in severity order: 🔴 Blocker, 🟠 Medium risk, 🟡 Low risk, 🔵 Nit. Use the same labels in the local file and published body. On re-review, match prior findings by problem and mark `NEW`, `STILL OPEN`, or `FIXED` with evidence.

Write `manifest.json`'s `review_file`: title and reviewed SHA/date; a summary with test results and limits; `## Findings` with `path:line`, severity, consequence, and fix (or `No findings.`); and one current `## Out of scope / notes`. On re-review, replace findings and prepend a `## Changes since last review` table of status transitions; keep older change sections.

## Publish

For a PR, choose `REQUEST_CHANGES`, `APPROVE`, or `COMMENT`. Draft the body using [the request-changes template](templates/request-changes.md) when appropriate. Put `{{code:path:L10-L15}}` on its own line after each current-code finding, or `{{base-code:path:L10-L15}}` for removed code. Run `python3 <skill-dir>/scripts/review_pr.py format --bundle DIR --draft FILE`; it validates ranges and writes bare Gitea commit permalinks to `body.md` for rendered code previews. Review the resulting body and test evidence.

Show the complete review to the user. Re-read the PR head and base through `gitea`, then run `python3 <skill-dir>/scripts/review_pr.py preflight --bundle DIR --current-pr-head SHA --current-pr-base BRANCH`. If refs changed, review again. Submit one review through `gitea` within existing authorization; otherwise present the complete draft for approval. Read back the verdict, body, and rendered previews. Report the local file, PR URL, and result. A branch without a PR produces only the local review.
