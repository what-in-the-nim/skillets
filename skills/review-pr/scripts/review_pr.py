#!/usr/bin/env python3
"""Prepare a PR review bundle and validate its published body."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote, urlsplit


CODE_MARKER = re.compile(r"\{\{(code|base-code):([^:{}]+):L(\d+)-L(\d+)\}\}")


def git(*args):
    """Run Git without copying successful output to the model context."""
    result = subprocess.run(["git", *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip() or "git failed")
    return result.stdout


def lookup(args):
    """Fetch one PR through the repository's remote and save its checked response."""
    remote_url = git("remote", "get-url", args.remote).decode().strip()
    if "://" in remote_url:
        repo_path = urlsplit(remote_url).path.lstrip("/")
    else:
        repo_path = remote_url.partition(":")[2]
    repo_path = repo_path.removesuffix(".git")
    if len(repo_path.split("/")) != 2 or not all(repo_path.split("/")):
        raise ValueError(f"cannot derive owner/repo from {args.remote} remote")
    result = subprocess.run(
        ["tea", "api", "--remote", args.remote, f"repos/{repo_path}/pulls/{args.number}"],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip() or "tea api failed")
    pr = json.loads(result.stdout)
    if not isinstance(pr, dict) or pr.get("message") or not all(key in pr for key in ("title", "head", "base")):
        raise ValueError(f"Gitea PR lookup failed: {pr.get('message', 'invalid response') if isinstance(pr, dict) else 'invalid response'}")
    try:
        summary = {
            "title": pr["title"], "head": pr["head"]["sha"],
            "head_ref": pr["head"]["ref"], "base": pr["base"]["ref"],
            "repo_url": pr["base"]["repo"]["html_url"], "pr_file": args.output,
        }
        base_repo = pr["base"]["repo"]["full_name"]
    except (KeyError, TypeError):
        raise ValueError("Gitea PR response is missing required fields") from None
    if base_repo != repo_path:
        raise ValueError("Gitea PR base repository differs from the selected remote")
    Path(args.output).write_bytes(result.stdout)
    print(json.dumps(summary))


def ref_sha(ref):
    """Resolve a ref to a full commit SHA."""
    if ref.startswith("-"):
        raise ValueError("ref cannot start with '-'")
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()


def refresh(ref):
    """Refresh a remote-tracking ref before comparing it."""
    remote, separator, branch = ref.partition("/")
    if separator and remote in git("remote").decode().splitlines():
        git("fetch", remote, branch)


def load_bundle(directory):
    """Read a prepared bundle and check its expected files."""
    path = Path(directory).resolve()
    manifest = json.loads((path / "manifest.json").read_text())
    if Path(manifest["root"]) != Path(git("rev-parse", "--show-toplevel").decode().strip()):
        raise ValueError("run from the repository used by prepare")
    return path, manifest


def prepare(args):
    """Store the exact comparison, changed-file list, and doc paths."""
    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    os.chdir(root)
    if args.expected_head and not args.repo_url:
        raise ValueError("--repo-url is required with --expected-head")
    if args.expected_head:
        remotes = git("remote").decode().splitlines()
        for label, ref in (("source", args.source), ("target", args.target)):
            if not any(ref.startswith(f"{remote}/") for remote in remotes):
                raise ValueError(f"PR {label} must be a remote-tracking ref such as origin/{ref}")
    refresh(args.target)
    refresh(args.source)
    source_sha, target_sha = ref_sha(args.source), ref_sha(args.target)
    if args.expected_head and source_sha != args.expected_head:
        raise ValueError("source ref differs from the Gitea PR head")
    comparison = f"{args.target}...{args.source}"
    changed = [os.fsdecode(p) for p in git("diff", "--name-only", "-z", comparison).split(b"\0") if p]
    docs = [root / name for name in ("CONTEXT.md", "INTEGRATION.md", "README.md")]
    docs += [root / name / "README.md" for name in sorted({p.split("/", 1)[0] for p in changed if "/" in p})]
    bundle = Path(tempfile.mkdtemp(prefix="review-pr-"))
    (bundle / "diff.patch").write_bytes(git("diff", comparison))
    (bundle / "files.txt").write_bytes(git("diff", "--name-status", comparison))
    (bundle / "commits.txt").write_bytes(git("log", f"{args.target}..{args.source}", "--oneline"))
    manifest = {
        "root": str(root), "source": args.source, "target": args.target,
        "source_sha": source_sha, "target_sha": target_sha,
        "expected_head": args.expected_head, "repo_url": args.repo_url,
        "changed_files": changed, "docs": [str(p) for p in docs if p.is_file()],
        "review_file": str(root / "review-notes" / f"{args.source.replace('/', '-')}-vs-{args.target.replace('/', '-')}.md"),
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(bundle)


def intake(args):
    """Summarize saved Gitea responses and verify changed-file coverage."""
    bundle, manifest = load_bundle(args.bundle)

    def read_json(name):
        """Read one saved Gitea response from the prepared bundle."""
        return json.loads((bundle / name).read_text())

    pr = read_json("pr.json")
    files = read_json("gitea-files.json")
    reviews = read_json("reviews.json")
    discussion = read_json("discussion.json")
    inline = read_json("inline.json")
    if pr["head"]["sha"] != manifest["source_sha"] or pr["base"]["ref"] != manifest["target"].split("/", 1)[-1]:
        raise ValueError("Gitea PR refs differ from the prepared bundle; review the current PR")
    if not all(isinstance(items, list) for items in (files, reviews, discussion, inline)):
        raise ValueError("Gitea files, reviews, and comments responses must be lists")
    api_files = {item["filename"] for item in files}
    prepared_files = set(manifest["changed_files"])
    if api_files != prepared_files:
        raise ValueError(f"Gitea file list differs from prepared diff: missing={sorted(prepared_files - api_files)}, extra={sorted(api_files - prepared_files)}")
    if not (bundle / "gitea.diff").read_bytes():
        raise ValueError("Gitea PR diff is empty")
    print(json.dumps({
        "title": pr["title"], "head": pr["head"]["sha"], "base": pr["base"]["ref"],
        "changed_files": manifest["changed_files"],
        "review_ids": [item["id"] for item in reviews],
        "discussion_comments": len(discussion), "inline_comments": len(inline),
    }))


def format_body(args):
    """Replace code markers with verified Gitea preview permalinks."""
    bundle, manifest = load_bundle(args.bundle)
    output = bundle / "body.md"
    output.unlink(missing_ok=True)
    repo_url = manifest["repo_url"]
    if not repo_url or urlsplit(repo_url).scheme not in ("http", "https") or not urlsplit(repo_url).netloc:
        raise ValueError("prepare with the Gitea repository web URL before formatting")
    draft = Path(args.draft).read_text()

    def replace(match):
        """Resolve one marker against the reviewed commit's file content."""
        line_start = draft.rfind("\n", 0, match.start()) + 1
        line_end = draft.find("\n", match.end())
        line_end = len(draft) if line_end < 0 else line_end
        if draft[line_start:line_end].strip() != match.group():
            raise ValueError("put each code marker on its own line")
        kind, path, start_text, end_text = match.groups()
        start, end = int(start_text), int(end_text)
        if start < 1 or end < start or end - start >= 20:
            raise ValueError(f"invalid code range: {match.group()}")
        sha = manifest["source_sha"] if kind == "code" else manifest["target_sha"]
        content = git("show", f"{sha}:{path}")
        if b"\0" in content or end > len(content.splitlines()):
            raise ValueError(f"code range is absent or binary: {match.group()}")
        return f"{repo_url.rstrip('/')}/src/commit/{sha}/{quote(path, safe='/')}#L{start}-L{end}"

    body = CODE_MARKER.sub(replace, draft)
    if "{{" in body or "}}" in body:
        raise ValueError("unresolved placeholder in draft")
    output.write_text(body)
    print(output)


def preflight(args):
    """Stop publication when a reviewed ref or PR head has changed."""
    bundle, manifest = load_bundle(args.bundle)
    refresh(manifest["target"])
    refresh(manifest["source"])
    if ref_sha(manifest["source"]) != manifest["source_sha"]:
        raise ValueError("source changed; review the new diff")
    if ref_sha(manifest["target"]) != manifest["target_sha"]:
        raise ValueError("target changed; review the new diff")
    if manifest["expected_head"]:
        if not args.current_pr_head:
            raise ValueError("re-read the PR through gitea and pass --current-pr-head")
        if not args.current_pr_base:
            raise ValueError("re-read the PR through gitea and pass --current-pr-base")
        if args.current_pr_head != manifest["expected_head"]:
            raise ValueError("Gitea PR head changed; review the new diff")
        if args.current_pr_base != manifest["target"].split("/", 1)[-1]:
            raise ValueError("Gitea PR base changed; review the new diff")
    if not (bundle / "body.md").is_file():
        raise ValueError("format the review body before preflight")
    print("ready")


def main():
    """Dispatch a quiet, deterministic review preparation command."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pr_lookup = commands.add_parser("lookup")
    pr_lookup.add_argument("--number", type=int, required=True)
    pr_lookup.add_argument("--remote", default="origin")
    pr_lookup.add_argument("--output", required=True)
    pr_lookup.set_defaults(action=lookup)
    prep = commands.add_parser("prepare")
    prep.add_argument("--source", required=True)
    prep.add_argument("--target", default="origin/dev")
    prep.add_argument("--expected-head")
    prep.add_argument("--repo-url")
    prep.set_defaults(action=prepare)
    summary = commands.add_parser("intake")
    summary.add_argument("--bundle", required=True)
    summary.set_defaults(action=intake)
    fmt = commands.add_parser("format")
    fmt.add_argument("--bundle", required=True)
    fmt.add_argument("--draft", required=True)
    fmt.set_defaults(action=format_body)
    check = commands.add_parser("preflight")
    check.add_argument("--bundle", required=True)
    check.add_argument("--current-pr-head")
    check.add_argument("--current-pr-base")
    check.set_defaults(action=preflight)
    args = parser.parse_args()
    try:
        args.action(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
