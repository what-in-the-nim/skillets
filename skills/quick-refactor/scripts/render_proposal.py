#!/usr/bin/env python3
"""Compile proposal JSON and Mermaid files into a validated, offline HTML report."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CORE = {"recommendation", "process", "target-design", "evidence", "validation", "first-pr"}
TOKEN = re.compile(r"\{\{[^{}]+\}\}")
EVIDENCE = {"reproduced behavior", "source-supported risk", "proposed improvement"}


def require_keys(value: dict, required: set, optional: set = frozenset()) -> None:
    """Reject missing or unknown fields instead of silently dropping report edits."""
    if not isinstance(value, dict):
        raise ValueError("expected an object")
    missing, extra = required - value.keys(), value.keys() - required - optional
    if missing or extra:
        raise ValueError(f"invalid fields: missing {sorted(missing)}, unknown {sorted(extra)}")


def text(value: str) -> str:
    """Escape a nonempty plain-text field."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected nonempty text")
    return html.escape(value, quote=True)


def diagram(reference: str, directory: Path, overview: bool = False) -> str:
    """Load a diagram from the content file's directory and enforce overview syntax."""
    if not isinstance(reference, str) or not reference.startswith("@") or not reference.endswith(".mmd"):
        raise ValueError("diagrams must reference @relative/path.mmd files")
    if Path(reference[1:]).is_absolute():
        raise ValueError("diagram references must be relative to the content file")
    source = (directory / reference[1:]).read_text(encoding="utf-8")
    if overview and not re.search(r"^\s*(flowchart|graph)\s", source, re.MULTILINE):
        raise ValueError("process diagrams must be before/after flowcharts")
    return f'<div class="diagram"><pre class="mermaid">{text(source)}</pre></div>'


def build_report(data: dict, directory: Path) -> str:
    """Generate all sections, navigation, and numbering from the content source."""
    require_keys(data, {"title", "target", "revision", "date", "sections"})
    sections = data["sections"]
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections must be a nonempty array")
    ids, navigation, rendered = [], [], []
    for index, section in enumerate(sections, 1):
        require_keys(section, {"id", "title"}, {"body_html", "diagrams", "evidence", "collapsed"})
        identifier = section["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", identifier):
            raise ValueError("section id must be a lowercase slug")
        if identifier in ids:
            raise ValueError(f"duplicate section id: {identifier}")
        ids.append(identifier)
        title = text(section["title"])
        body = section.get("body_html", "")
        if not isinstance(body, str):
            raise ValueError("body_html must be a string")
        pair = section.get("diagrams")
        if pair is not None:
            require_keys(pair, {"before", "after"})
            body += '<div class="diagram-pair">'
            for key, caption in (("before", "Before"), ("after", "Target design")):
                body += f'<figure class="diagram-card"><figcaption>{caption}</figcaption>{diagram(pair[key], directory, identifier == "process")}</figure>'
            body += '</div>'
        if identifier == "process" and pair is None:
            raise ValueError("process requires paired before/after flowcharts")
        evidence = section.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("evidence must be an array")
        if identifier == "evidence" and not evidence:
            raise ValueError("evidence section requires labeled evidence entries")
        for entry in evidence:
            require_keys(entry, {"strength", "text", "source"})
            if entry["strength"] not in EVIDENCE:
                raise ValueError(f"unknown evidence strength: {entry['strength']}")
            body += f'<p><strong>{text(entry["strength"])}:</strong> {text(entry["text"])} <span class="meta">{text(entry["source"])}</span></p>'
        if not body.strip():
            raise ValueError(f"empty section: {identifier}")
        collapsed = section.get("collapsed", False)
        if not isinstance(collapsed, bool):
            raise ValueError("collapsed must be a boolean")
        if collapsed and identifier in {"recommendation", "process", "target-design", "first-pr"}:
            raise ValueError(f"core overview must remain visible: {identifier}")
        if collapsed:
            body = f'<details><summary>Show {title}</summary>{body}</details>'
        navigation.append(f'<a href="#{identifier}">{title}</a>')
        rendered.append(f'<section id="{identifier}" aria-labelledby="{identifier}-title"><h2 id="{identifier}-title">{index}. {title}</h2><div class="content">{body}</div></section>')
    if CORE - set(ids):
        raise ValueError(f"missing core sections: {sorted(CORE - set(ids))}")
    if ids[:2] != ["recommendation", "process"]:
        raise ValueError("lead with recommendation, then process")
    values = {key.upper(): text(data[key]) for key in ("title", "target", "revision", "date")}
    values.update(NAV_HTML="".join(navigation), SECTIONS_HTML="\n".join(rendered))
    template = (SKILL / "templates/proposal.html").read_text(encoding="utf-8")
    result = TOKEN.sub(lambda match: values[match.group()[2:-2]], template)
    if TOKEN.search(result):
        raise ValueError("unresolved template token in report content")
    return result


def find_browser(explicit: str | None) -> str:
    """Locate an installed browser without downloading anything at render time."""
    candidates = [explicit or os.environ.get("CHROME_PATH", ""),
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "chromium", "chromium-browser", "google-chrome", "chrome"]
    for candidate in candidates:
        if candidate and (resolved := shutil.which(candidate)):
            return resolved
    raise ValueError("Chrome/Chromium required: pass --browser or set CHROME_PATH; no download was attempted")


def compile_report(document: str, browser: str) -> str:
    """Compile with bundled Mermaid, validate the DOM, and return static HTML."""
    mermaid = (SKILL / "vendor/mermaid-11.12.0.min.js").read_text(encoding="utf-8")
    runner = (SKILL / "scripts/compile_diagrams.js").read_text(encoding="utf-8")
    scripts = f'<script>{mermaid}</script><script>{runner}</script>'
    with tempfile.TemporaryDirectory(prefix="quick-refactor-") as temporary:
        root = Path(temporary)
        source = root / "source.html"
        source.write_text(document.replace("</body>", scripts + "</body>"), encoding="utf-8")
        command = [browser, "--headless=new", "--disable-gpu", "--disable-background-networking",
                   "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                   "--host-resolver-rules=MAP * ~NOTFOUND", f"--user-data-dir={root / 'profile'}",
                   "--virtual-time-budget=30000", "--dump-dom", source.as_uri()]
        dump, errors = root / "dump.html", root / "browser.log"
        with dump.open("w") as stdout, errors.open("w") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    output = dump.read_text(encoding="utf-8")
                    if output.rstrip().endswith("</html>") or process.poll() is not None:
                        break
                    time.sleep(0.1)
            finally:
                # Chrome helpers may hold pipes open after the DOM dump is complete.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        output = dump.read_text(encoding="utf-8")
        diagnostics = errors.read_text(encoding="utf-8")[-1500:]
    failure = re.search(r'data-render-error="([^"]*)"', output)
    if failure:
        raise ValueError(html.unescape(failure.group(1)))
    if not output.rstrip().endswith("</html>") or 'data-render-status="complete"' not in output:
        raise ValueError("offline diagram compilation did not complete: " + diagnostics)
    if re.search(r"<script\b", output, re.IGNORECASE) or TOKEN.search(output):
        raise ValueError("unexpected script or unresolved token in compiled report")
    return output


def main() -> None:
    """Validate and compile before atomically replacing the report artifact."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="proposal JSON; see ../examples/proposal.json")
    parser.add_argument("-o", "--output", type=Path, help="default: beside JSON with .html suffix")
    parser.add_argument("--browser", help="Chrome/Chromium executable (or CHROME_PATH)")
    args = parser.parse_args()
    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
        document = build_report(data, args.data.resolve().parent)
        output = args.output or args.data.with_suffix(".html")
        if output.resolve() == args.data.resolve() or output.suffix.lower() != ".html":
            raise ValueError("output must be an .html file distinct from the content source")
        compiled = compile_report(document, find_browser(args.browser))
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(compiled)
        try:
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Validated offline report: {output.resolve()}")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Render failed: {error}\n")


if __name__ == "__main__":
    main()
