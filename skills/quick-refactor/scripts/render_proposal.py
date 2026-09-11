#!/usr/bin/env python3
"""Render a compact JSON quick-refactor proposal into the HTML template."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def parse_args() -> argparse.Namespace:
    """Parse renderer command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="JSON file containing template token values")
    parser.add_argument("-o", "--output", type=Path, help="HTML output path")
    return parser.parse_args()


def load_data(path: Path) -> dict[str, Any]:
    """Load and validate the proposal data object from JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("proposal data must be a JSON object")
    return data


def render(template: str, data: dict[str, Any]) -> str:
    """Substitute every template token exactly once with validated values."""
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

    def replace(match: re.Match[str]) -> str:
        """Escape text values while preserving explicitly supplied HTML fragments."""
        token = match.group(1)
        value = data[token]
        if not isinstance(value, str):
            raise ValueError(f"value for {token} must be a string")
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
    output = args.output or Path(f"quick-refactor-{slugify(title)}.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(template_path.read_text(encoding="utf-8"), data), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
