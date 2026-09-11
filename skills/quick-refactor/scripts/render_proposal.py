#!/usr/bin/env python3
"""Render a compact JSON quick-refactor proposal into the HTML template."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
MERMAID_TOKENS = {
    "CURRENT_CLASS_MERMAID",
    "PROPOSED_CLASS_MERMAID",
    "CURRENT_SEQUENCE_MERMAID",
    "PROPOSED_SEQUENCE_MERMAID",
}


def parse_args() -> argparse.Namespace:
    """Parse renderer command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="JSON file containing template token values")
    parser.add_argument("-o", "--output", type=Path, help="HTML output path")
    parser.add_argument("--check-mermaid", action="store_true", help="validate diagrams with mmdc when installed")
    return parser.parse_args()


def load_data(path: Path) -> dict[str, Any]:
    """Load and validate the proposal data object from JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("proposal data must be a JSON object")
    return data


def resolve_data(data: dict[str, Any], data_dir: Path) -> dict[str, Any]:
    """Load Mermaid file references and return render-ready proposal data."""
    resolved = data.copy()
    for token in MERMAID_TOKENS:
        value = resolved[token]
        if not isinstance(value, str):
            raise ValueError(f"value for {token} must be a string")
        if value.startswith("@"):
            resolved[token] = (data_dir / value[1:]).read_text(encoding="utf-8")
    return resolved


def validate_mermaid(data: dict[str, Any], data_dir: Path) -> None:
    """Validate diagrams with Mermaid CLI when the optional tool is available."""
    executable = shutil.which("mmdc")
    if executable is None:
        print("Mermaid validation: skipped (mmdc not found)")
        return
    resolved = resolve_data(data, data_dir)
    with tempfile.TemporaryDirectory() as directory:
        directory_path = Path(directory)
        for token in MERMAID_TOKENS:
            source = directory_path / f"{token}.mmd"
            output = directory_path / f"{token}.svg"
            source.write_text(resolved[token], encoding="utf-8")
            result = subprocess.run(
                [executable, "-i", str(source), "-o", str(output)],
                capture_output=True,
                text=True,
            )
            if result.returncode:
                detail = result.stderr.strip() or result.stdout.strip() or "unknown Mermaid error"
                raise ValueError(f"{token} failed Mermaid validation: {detail}")
    print("Mermaid validation: ok")


def render(template: str, data: dict[str, Any], data_dir: Path) -> str:
    """Substitute every template token once, loading referenced diagrams."""
    tokens = set(TOKEN_PATTERN.findall(template))
    missing = tokens - data.keys()
    extra = data.keys() - tokens
    if missing or extra:
        problems = []
        if missing:
            problems.append(f"missing: {', '.join(sorted(missing))}")
        if extra:
            problems.append(f"unknown: {', '.join(sorted(extra))}")
        raise ValueError("invalid proposal data (" + "; ".join(problems) + ")")
    data = resolve_data(data, data_dir)

    def replace(match: re.Match[str]) -> str:
        """Escape text values while preserving explicitly supplied HTML fragments."""
        token = match.group(1)
        value = data[token]
        if not isinstance(value, str):
            raise ValueError(f"value for {token} must be a string")
        if token in MERMAID_TOKENS and value.startswith("@"):
            value = (data_dir / value[1:]).read_text(encoding="utf-8")
        return value if token.endswith("_HTML") else html.escape(value)

    return TOKEN_PATTERN.sub(replace, template)


def slugify(title: str) -> str:
    """Create a filesystem-friendly slug from a proposal title."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "proposal"


def main() -> None:
    """Render the proposal and write its HTML artifact."""
    args = parse_args()
    template_path = Path(__file__).resolve().parent.parent / "templates" / "proposal.html"
    data = load_data(args.data)
    title = data.get("TITLE")
    if not isinstance(title, str):
        raise ValueError("TITLE must be a string")
    if args.check_mermaid:
        validate_mermaid(data, args.data.parent)
    output = args.output or Path(f"quick-refactor-{slugify(title)}.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render(template_path.read_text(encoding="utf-8"), data, args.data.parent), encoding="utf-8"
    )
    print(output)


if __name__ == "__main__":
    main()
