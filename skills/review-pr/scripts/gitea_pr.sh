#!/usr/bin/env bash
# Gitea PR helper for the review-pr skill.
#
# Usage:
#   gitea_pr.sh meta   <pr-number>
#   gitea_pr.sh files  <pr-number>
#   gitea_pr.sh diff   <pr-number>
#   gitea_pr.sh review <pr-number> <REQUEST_CHANGES|APPROVE|COMMENT> <body-file.md>
#
# Auth: uses HTTP basic auth from ~/.netrc (curl -n), which works for private repos.
# Connection: GITEA_URL from repo .env; owner/repo derived from the origin remote.
set -euo pipefail

cmd="${1:-}"
pr="${2:-}"

# Resolve repo root (the git toplevel) so .env and the remote are found regardless of cwd.
ROOT="$(git rev-parse --show-toplevel)"

# GITEA_URL from .env (fallback to env var if already exported).
if [[ -f "$ROOT/.env" ]]; then
  GITEA_URL="$(grep -E '^GITEA_URL=' "$ROOT/.env" | head -1 | cut -d= -f2- | tr -d '"'"'"'' )"
fi
GITEA_URL="${GITEA_URL:-${GITEA_URL_ENV:-}}"
BASE="${GITEA_URL%/}"
[[ -n "$BASE" ]] || { echo "ERROR: GITEA_URL not found in $ROOT/.env or environment" >&2; exit 1; }

py() { python3 -c "$1" "${@:2}"; }

# owner/repo from origin remote: git@host:owner/repo.git  or  https://host/owner/repo.git
REMOTE="$(git -C "$ROOT" remote get-url origin)"
OWNER_REPO="$(py '
import re,sys
m=re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", sys.argv[1])
print(m.group(1) if m else "")
' "$REMOTE")"
[[ -n "$OWNER_REPO" ]] || { echo "ERROR: could not parse owner/repo from remote: $REMOTE" >&2; exit 1; }
API="$BASE/api/v1/repos/$OWNER_REPO"

case "$cmd" in
  meta)
    [[ -n "$pr" ]] || { echo "usage: gitea_pr.sh meta <pr-number>" >&2; exit 2; }
    curl -s -n "$API/pulls/$pr" | py '
import sys,json
d=json.load(sys.stdin)
if d.get("number") is None:
    print("ERROR:", d.get("message","unexpected response"), file=sys.stderr); sys.exit(1)
print("#%s %s" % (d["number"], d["title"]))
print("state=%s mergeable=%s +%s/-%s files=%s" % (d["state"], d.get("mergeable"), d.get("additions"), d.get("deletions"), d.get("changed_files")))
print("head=%s base=%s" % (d["head"]["ref"], d["base"]["ref"]))
print("\n=== BODY ===\n" + (d.get("body") or "(empty)"))
'
    ;;
  files)
    [[ -n "$pr" ]] || { echo "usage: gitea_pr.sh files <pr-number>" >&2; exit 2; }
    curl -s -n "$API/pulls/$pr/files?limit=100" | py '
import sys,json
for f in json.load(sys.stdin):
    print("%9s  +%s/-%s  %s" % (f["status"], f.get("additions"), f.get("deletions"), f["filename"]))
'
    ;;
  diff)
    [[ -n "$pr" ]] || { echo "usage: gitea_pr.sh diff <pr-number>" >&2; exit 2; }
    curl -s -n "$API/pulls/$pr.diff"
    ;;
  review)
    event="${3:-}"; body_file="${4:-}"
    [[ -n "$pr" && -n "$event" && -n "$body_file" ]] || { echo "usage: gitea_pr.sh review <pr-number> <REQUEST_CHANGES|APPROVE|COMMENT> <body-file.md>" >&2; exit 2; }
    [[ -f "$body_file" ]] || { echo "ERROR: body file not found: $body_file" >&2; exit 1; }
    payload="$(py 'import json,sys; print(json.dumps({"body":open(sys.argv[1]).read(),"event":sys.argv[2]}))' "$body_file" "$event")"
    echo "$payload" | curl -s -n -X POST -H "Content-Type: application/json" --data-binary @- \
      "$API/pulls/$pr/reviews" | py '
import sys,json
d=json.load(sys.stdin)
if "id" not in d:
    print("ERROR:", d.get("message","post failed"), file=sys.stderr); sys.exit(1)
print("posted review id=%s state=%s" % (d["id"], d.get("state")))
print("url: %s" % d.get("html_url"))
'
    ;;
  *)
    echo "usage: gitea_pr.sh {meta|files|diff|review} <pr-number> [args]" >&2
    exit 2
    ;;
esac
