#!/usr/bin/env python3
"""Exercise offline rendering, reproducible edits, and failed-render preservation."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from render_proposal import SKILL, build_report


def main() -> None:
    """Run a dependency-free regression check against the bundled example."""
    example = json.loads((SKILL / "examples/proposal.json").read_text())
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for source in (SKILL / "examples").glob("*.mmd"):
            shutil.copy(source, root)
        content, output = root / "proposal.json", root / "report.html"

        def run(data: dict, succeeds: bool = True) -> str:
            """Invoke the public command from outside the skill or project directory."""
            content.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(SKILL / "scripts/render_proposal.py"),
                                     str(content), "-o", str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=70)
            assert (result.returncode == 0) == succeeds, result.stdout + result.stderr
            return output.read_text() if output.exists() else ""

        first = run(example)
        assert first.count('<svg ') == 6
        assert '<script' not in first and 'cdn.jsdelivr' not in first
        assert 'data-render-status="complete"' in first
        edited = copy.deepcopy(example)
        edited['sections'] = [s for s in edited['sections'] if s['id'] not in {'ownership', 'timing'}]
        edited['sections'].insert(2, {'id': 'follow-up', 'title': 'Follow-up',
                                      'body_html': '<p>Persistent follow-up edit.</p>'})
        second = run(edited)
        assert second.count('<svg ') == 2 and 'Persistent follow-up edit.' in second
        assert '3. Follow-up' in second and 'href="#follow-up"' in second
        assert run(edited).count('Persistent follow-up edit.') == 1
        stable = output.read_bytes()
        edited['sections'][2]['body_html'] = '<a href="#missing">Broken navigation</a>'
        run(edited, succeeds=False)
        assert output.read_bytes() == stable
        edited['sections'][2]['body_html'] = '<p id="recommendation">Duplicate ID</p>'
        run(edited, succeeds=False)
        assert output.read_bytes() == stable
        edited['sections'][2]['body_html'] = '<p>Restored</p>'
        (root / 'after.mmd').write_text('flowchart TD\n A --> [invalid')
        run(edited, succeeds=False)
        assert output.read_bytes() == stable
        for mutate in (
            lambda d: d['sections'].pop(),
            lambda d: d['sections'].append(d['sections'][0]),
            lambda d: d.update(typo='must not disappear'),
            lambda d: d['sections'][0].update(body_html='{{UNRESOLVED}}'),
            lambda d: d['sections'][5]['evidence'][0].update(strength='confirmed bug'),
        ):
            invalid = copy.deepcopy(example)
            mutate(invalid)
            try:
                build_report(invalid, SKILL / 'examples')
            except ValueError:
                pass
            else:
                raise AssertionError('invalid content was accepted')
    print('Passed: offline diagrams, follow-up edits, optional sections, and failure preservation')


if __name__ == '__main__':
    main()
