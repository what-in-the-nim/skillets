"""Exercise the review bundle, permalink formatter, and stale-ref gate."""

from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


SCRIPT = Path(__file__).with_name("review_pr.py")
SPEC = importlib.util.spec_from_file_location("review_pr", SCRIPT)
review_pr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review_pr)


class ReviewPrTest(unittest.TestCase):
    """Check the CLI against a small repository and local remote."""

    def test_lookup_uses_remote_owner_and_rejects_api_errors(self):
        """Resolve the repository from Git and save only a valid PR response."""
        pr = {
            "title": "Change", "head": {"sha": "abc", "ref": "feature"},
            "base": {"ref": "dev", "repo": {"full_name": "owner/repo", "html_url": "https://git.example/owner/repo"}},
        }
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "pr.json"
            args = SimpleNamespace(remote="origin", number=42, output=str(output))
            for remote_url in (b"git@git.example:owner/repo.git\n", b"https://git.example/owner/repo.git\n"):
                with mock.patch.object(review_pr, "git", return_value=remote_url), mock.patch.object(
                    review_pr.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(pr).encode(), b"")
                ) as api, redirect_stdout(StringIO()) as printed:
                    review_pr.lookup(args)
                self.assertEqual(api.call_args.args[0][2:4], ["--remote", "origin"])
                self.assertEqual(api.call_args.args[0][-1], "repos/owner/repo/pulls/42")
                self.assertEqual(json.loads(printed.getvalue())["head"], "abc")
                self.assertEqual(json.loads(output.read_text()), pr)

            output.unlink()
            with mock.patch.object(review_pr, "git", return_value=b"git@git.example:owner/repo.git\n"), mock.patch.object(
                review_pr.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b'{"message":"not found"}', b"")
            ), self.assertRaisesRegex(ValueError, "not found"):
                review_pr.lookup(args)
            self.assertFalse(output.exists())

            pr["base"]["repo"]["full_name"] = "other/repo"
            with mock.patch.object(review_pr, "git", return_value=b"git@git.example:owner/repo.git\n"), mock.patch.object(
                review_pr.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(pr).encode(), b"")
            ), self.assertRaisesRegex(ValueError, "differs from the selected remote"):
                review_pr.lookup(args)
            self.assertFalse(output.exists())

    def test_bundle_preview_and_stale_target(self):
        """Keep preparation quiet and stop posting after the base moves."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            remote, work = root / "remote.git", root / "work"

            def run(*args, cwd=None, ok=True):
                """Run one local Git or skill command with captured output."""
                result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
                if ok:
                    self.assertEqual(result.returncode, 0, result.stderr)
                else:
                    self.assertNotEqual(result.returncode, 0)
                return result.stdout.strip(), result.stderr.strip()

            run("git", "init", "--bare", str(remote))
            run("git", "clone", str(remote), str(work))
            run("git", "config", "user.name", "Review Test", cwd=work)
            run("git", "config", "user.email", "review@example.test", cwd=work)
            run("git", "checkout", "-b", "dev", cwd=work)
            (work / "README.md").write_text("Repository context\n")
            (work / "app.py").write_text("first\n")
            run("git", "add", ".", cwd=work)
            run("git", "commit", "-m", "base", cwd=work)
            run("git", "push", "-u", "origin", "dev", cwd=work)
            run("git", "checkout", "-b", "feature", cwd=work)
            (work / "app.py").write_text("first\nsecond\n")
            run("git", "commit", "-am", "change", cwd=work)
            head, _ = run("git", "rev-parse", "HEAD", cwd=work)
            run("git", "push", "-u", "origin", "feature", cwd=work)

            _, error = run(sys.executable, str(SCRIPT), "prepare", "--source", "feature",
                           "--expected-head", head, "--repo-url", "https://git.example/o/r", cwd=work, ok=False)
            self.assertIn("remote-tracking ref", error)
            bundle_text, _ = run(sys.executable, str(SCRIPT), "prepare", "--source", "origin/feature",
                                 "--expected-head", head, "--repo-url", "https://git.example/o/r", cwd=work)
            bundle = Path(bundle_text)
            self.addCleanup(shutil.rmtree, bundle, True)
            self.assertEqual(len(bundle_text.splitlines()), 1)
            self.assertIn("app.py", (bundle / "files.txt").read_text())
            self.assertIn("+second", (bundle / "diff.patch").read_text())
            for name, value in {
                "pr.json": {"title": "Change", "head": {"sha": head}, "base": {"ref": "dev"}},
                "gitea-files.json": [{"filename": "app.py"}],
                "reviews.json": [{"id": 12}],
                "discussion.json": [{}],
                "inline.json": [],
            }.items():
                (bundle / name).write_text(json.dumps(value))
            (bundle / "gitea.diff").write_bytes((bundle / "diff.patch").read_bytes())
            summary_text, _ = run(sys.executable, str(SCRIPT), "intake", "--bundle", str(bundle), cwd=work)
            summary = json.loads(summary_text)
            self.assertEqual(summary["changed_files"], ["app.py"])
            self.assertEqual(summary["review_ids"], [12])
            self.assertEqual(summary["discussion_comments"], 1)
            (bundle / "gitea-files.json").write_text("[]")
            _, error = run(sys.executable, str(SCRIPT), "intake", "--bundle", str(bundle), cwd=work, ok=False)
            self.assertIn("file list differs", error)
            run("git", "remote", "add", "upstream", str(remote), cwd=work)
            other_text, _ = run(sys.executable, str(SCRIPT), "prepare", "--source", "feature",
                                "--target", "upstream/dev", cwd=work)
            other_bundle = Path(other_text)
            self.addCleanup(shutil.rmtree, other_bundle, True)
            self.assertIn('"target": "upstream/dev"', (other_bundle / "manifest.json").read_text())

            draft = root / "draft.md"
            draft.write_text("Fix this.\n\n{{code:app.py:L2-L2}}\n")
            body_path, _ = run(sys.executable, str(SCRIPT), "format", "--bundle", str(bundle),
                               "--draft", str(draft), cwd=work)
            self.assertIn(f"https://git.example/o/r/src/commit/{head}/app.py#L2-L2",
                          Path(body_path).read_text())
            draft.write_text("{{code:app.py:L3-L3}}\n")
            _, error = run(sys.executable, str(SCRIPT), "format", "--bundle", str(bundle),
                           "--draft", str(draft), cwd=work, ok=False)
            self.assertIn("code range is absent", error)
            self.assertFalse(Path(body_path).exists())
            draft.write_text("See {{code:app.py:L2-L2}} here.\n")
            _, error = run(sys.executable, str(SCRIPT), "format", "--bundle", str(bundle),
                           "--draft", str(draft), cwd=work, ok=False)
            self.assertIn("own line", error)
            draft.write_text("Fix this.\n\n{{code:app.py:L2-L2}}\n")
            run(sys.executable, str(SCRIPT), "format", "--bundle", str(bundle),
                "--draft", str(draft), cwd=work)
            ready, _ = run(sys.executable, str(SCRIPT), "preflight", "--bundle", str(bundle),
                           "--current-pr-head", head, "--current-pr-base", "dev", cwd=work)
            self.assertEqual(ready, "ready")

            run(sys.executable, str(SCRIPT), "preflight", "--bundle", str(bundle),
                "--current-pr-head", "0" * 40, "--current-pr-base", "dev", cwd=work, ok=False)
            run(sys.executable, str(SCRIPT), "preflight", "--bundle", str(bundle),
                "--current-pr-head", head, "--current-pr-base", "main", cwd=work, ok=False)
            run("git", "checkout", "dev", cwd=work)
            (work / "README.md").write_text("New base context\n")
            run("git", "commit", "-am", "move base", cwd=work)
            run("git", "push", "origin", "dev", cwd=work)
            _, error = run(sys.executable, str(SCRIPT), "preflight", "--bundle", str(bundle),
                           "--current-pr-head", head, "--current-pr-base", "dev", cwd=work, ok=False)
            self.assertIn("target changed", error)


if __name__ == "__main__":
    unittest.main()
