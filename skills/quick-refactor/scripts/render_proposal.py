#!/usr/bin/env python3
"""Render a structured refactor proposal as static HTML using only Python's standard library."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
STRENGTHS = {'reproduced behavior', 'source-supported risk', 'proposed improvement'}


def fields(value: dict, names: str, optional: str = '') -> None:
    """Require an exact object shape so misspelled fields cannot silently disappear."""
    expected = set(names.split())
    if not isinstance(value, dict) or not expected <= set(value) or set(value) - expected - set(optional.split()):
        raise ValueError(f'expected fields: {sorted(expected)}')


def string(value: str) -> str:
    """Validate nonempty plain text and escape it for HTML."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError('expected nonempty text')
    return html.escape(value, quote=True)


def strings(value: list, allow_empty: bool = False) -> str:
    """Render a list of plain-text statements without interpreting markup."""
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError('expected a list of statements')
    return '<ul>' + ''.join(f'<li>{string(item)}</li>' for item in value) + '</ul>'


def source(value: dict, repo: Path, check: bool) -> str:
    """Build a source link and optionally verify its path and line range."""
    fields(value, 'path line end_line')
    path = value['path']
    string(path)
    start, end = value['line'], value['end_line']
    if type(start) is not int or type(end) is not int or start < 1 or end < start:
        raise ValueError('source lines must be positive, ordered integers')
    if Path(path).is_absolute():
        raise ValueError('source paths must be repository-relative')
    absolute = (repo / path).resolve()
    if not absolute.is_relative_to(repo):
        raise ValueError('source path must stay inside repository')
    if check and (not absolute.is_file() or end > len(absolute.read_text(encoding='utf-8').splitlines())):
        raise ValueError(f'source path or line range unavailable: {path}:{start}-{end}')
    label = f'{path}:{start}' + (f'–{end}' if end != start else '')
    return f'<a href="{html.escape(str(absolute), quote=True)}:{start}">{string(label)}</a>'


def visualization(value: dict) -> str:
    """Render a content-selected flow, class, sequence, code comparison, or no diagram."""
    if not isinstance(value, dict):
        raise ValueError('visualization must be an object')
    kind = value.get('type')
    if kind == 'none':
        fields(value, 'type')
        return ''
    if kind == 'code':
        fields(value, 'type language before after')
        return code_pair(value)
    fields(value, 'type before after')
    panels = []
    for side, caption in [('before', 'Before'), ('after', 'Proposed')]:
        content = value[side]
        if kind == 'flow':
            strings(content)
            body = '<ol class="flow">' + ''.join(f'<li>{string(step)}</li>' for step in content) + '</ol>'
        elif kind == 'class':
            fields(content, 'classes relations')
            if not isinstance(content['classes'], list) or not content['classes']:
                raise ValueError('class diagram needs class records')
            names, cards = [], []
            for record in content['classes']:
                fields(record, 'name members')
                name = record['name']
                string(name)
                if name in names:
                    raise ValueError('duplicate class name')
                names.append(name)
                cards.append(f'<div class="class-box"><strong>{string(name)}</strong>{strings(record["members"], True)}</div>')
            if not isinstance(content['relations'], list):
                raise ValueError('class relations must be a list')
            relations = []
            for relation in content['relations']:
                fields(relation, 'from to label')
                if relation['from'] not in names or relation['to'] not in names:
                    raise ValueError('class relation references an unknown class')
                relations.append(f'<li><span class="relation-end">{string(relation["from"])}</span><span class="relation-link"><small>{string(relation["label"])}</small><span aria-hidden="true">⟶</span></span><span class="relation-end">{string(relation["to"])}</span></li>')
            body = '<div class="class-grid">' + ''.join(cards) + '</div><ul class="relations">' + ''.join(relations) + '</ul>'
        elif kind == 'sequence':
            fields(content, 'participants messages')
            actors = content['participants']
            strings(actors)
            if len(set(actors)) != len(actors) or not isinstance(content['messages'], list) or not content['messages']:
                raise ValueError('sequence needs unique participants and messages')
            events = [f'<div class="lifeline" aria-hidden="true" style="grid-column:{index};grid-row:2/{len(content["messages"]) + 2}"></div>' for index in range(1, len(actors) + 1)]
            for index, message in enumerate(content['messages'], 2):
                fields(message, 'from to label')
                if message['from'] not in actors or message['to'] not in actors:
                    raise ValueError('message references an unknown participant')
                origin, destination = actors.index(message['from']) + 1, actors.index(message['to']) + 1
                endpoints = f'{string(message["from"])} → {string(message["to"])}' if origin <= destination else f'{string(message["to"])} ← {string(message["from"])}'
                direction = 'forward' if origin < destination else 'return' if origin > destination else 'self-call'
                events.append(f'<div class="message {direction}" style="grid-column:{min(origin, destination)}/{max(origin, destination) + 1};grid-row:{index}"><span class="message-path">{endpoints}</span><strong>{string(message["label"])}</strong><span class="message-arrow" aria-hidden="true"></span></div>')
            body = f'<div class="sequence" style="grid-template-columns:repeat({len(actors)},minmax(100px,1fr))">' + ''.join(f'<div class="lane" style="grid-column:{index};grid-row:1">{string(actor)}</div>' for index, actor in enumerate(actors, 1)) + ''.join(events) + '</div>'
        else:
            raise ValueError('visualization type must be flow, class, sequence, code or none')
        panels.append(f'<article class="ownership {side}"><div class="eyebrow">{caption} · {string(kind)}</div>{body}</article>')
    return '<div class="pair visual-pair">' + ''.join(panels) + '</div>'


def code_pair(value: dict) -> str:
    """Display current and explicitly proposed code as escaped preformatted blocks."""
    language = string(value['language'])
    return '<div class="pair">' + ''.join(
        f'<article class="code-card"><div class="eyebrow">{caption} · {language}</div><pre><code>{string(value[key])}</code></pre></article>'
        for key, caption in [('before', 'Current source excerpt'), ('after', 'Proposed excerpt · not implemented')]
    ) + '</div>'


def detail_sections(design: dict, first: dict, version: int) -> str:
    """Render only the selected choice's detailed design and implementation scope."""
    if version == 3:
        fields(design, 'owner boundary interface invariants visualization lifecycle', 'code')
        visual = visualization(design['visualization'])
    else:
        fields(design, 'owner boundary interface invariants before after lifecycle', 'code')
        visual = visualization({'type': 'flow', 'before': design['before']['steps'], 'after': design['after']['steps']})
        for side in ['before', 'after']:
            fields(design[side], 'title responsibilities steps')
            visual += f'<div class="support-block"><h3>{string(design[side]["title"])}</h3>{strings(design[side]["responsibilities"])}</div>'
    code = ''
    if 'code' in design:
        fields(design['code'], 'language before after')
        code = '<section><h2>The change in code</h2>' + code_pair(design['code']) + '</section>'
    fields(first, 'summary files acceptance deferred')
    delivery = f'<section id="delivery"><h2>First useful PR</h2><p>{string(first["summary"])}</p><div class="support-block"><h3>Files, acceptance and deferred work</h3><h3>Files</h3>{strings(first["files"])}<h3>Acceptance</h3>{strings(first["acceptance"])}<h3>Deferred</h3>{strings(first["deferred"], True)}</div></section>'
    boundaries = f'<div class="support-block"><h3>Boundary, interface and preserved behavior</h3><p>{string(design["owner"])}</p><p>{string(design["boundary"])}</p><h3>Interface</h3>{strings(design["interface"])}<h3>Invariants</h3>{strings(design["invariants"])}<h3>Lifecycle</h3>{strings(design["lifecycle"], True)}</div>'
    return '<section id="design"><h2>Selected redesign</h2>' + visual + code + boundaries + '</section>' + delivery


def render(data: dict, check_sources: bool = False) -> tuple[str, str]:
    """Validate and render every authored field, preserving technical statements verbatim."""
    if not isinstance(data, dict):
        raise ValueError('proposal must be an object')
    version = data.get('schema_version')
    if type(version) is not int or version not in {2, 3}:
        raise ValueError('expected schema_version 2 or 3')
    stage = data.get('stage', 'design') if version == 3 else 'design'
    if stage not in {'choices', 'design'}:
        raise ValueError('stage must be choices or design')
    common = 'schema_version title target repository revision date evidence_status choices shorter_list_reason recommended_choice recommendation_reason evidence checks'
    extra = (' stage' + (' selected_choice design first_pr' if stage == 'design' else '')) if version == 3 else ' design first_pr'
    fields(data, common + extra)
    metadata = {key: string(data[key]) for key in ('title', 'target', 'repository', 'revision', 'date', 'evidence_status', 'recommendation_reason')}
    if not Path(data['repository']).is_absolute():
        raise ValueError('repository must be an absolute path')
    repo = Path(data['repository']).resolve()
    if check_sources:
        revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        if revision != data['revision']:
            raise ValueError('repository HEAD differs from recorded revision')
    choices = data['choices']
    if not isinstance(choices, list) or not 1 <= len(choices) <= 3:
        raise ValueError('expected one to three choices')
    reason = data['shorter_list_reason']
    if not isinstance(reason, str) or (len(choices) < 3 and not reason.strip()):
        raise ValueError('fewer than three choices require shorter_list_reason')
    ids, cards = [], []
    evidence = data['evidence']
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('expected evidence entries')
    evidence_ids, evidence_rows, covered = [], [], set()
    for entry in evidence:
        fields(entry, 'id choice_id strength confidence claim sources')
        identifier = entry['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', identifier) or identifier in evidence_ids:
            raise ValueError('evidence IDs must be unique lowercase slugs')
        evidence_ids.append(identifier)
        covered.add(string(entry['choice_id']))
        if entry['strength'] not in STRENGTHS:
            raise ValueError('unknown evidence strength')
        if not isinstance(entry['sources'], list) or (not entry['sources'] and check_sources):
            raise ValueError('real proposals require source references for every evidence entry')
        links = ' · '.join(source(ref, repo, check_sources) for ref in entry['sources'])
        evidence_rows.append(f'<article id="evidence-{identifier}"><h3>{string(entry["choice_id"])} · {string(entry["strength"])}</h3><p>{string(entry["claim"])}</p><p class="meta">{string(entry["confidence"])}</p><p>{links}</p></article>')
    recommended = None
    for choice in choices:
        fields(choice, 'id title friction benefit first_slice tradeoff evidence_ids' + (' visualization' if version == 3 else ''))
        identifier = choice['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', identifier) or identifier in ids:
            raise ValueError('choice IDs must be unique lowercase slugs')
        ids.append(identifier)
        if not isinstance(choice['evidence_ids'], list) or not choice['evidence_ids']:
            raise ValueError('each choice must link to evidence')
        for ref in choice['evidence_ids']:
            if ref not in evidence_ids or not any(e['id'] == ref and e['choice_id'] == identifier for e in evidence):
                raise ValueError('choice evidence reference is missing or belongs to another choice')
        selected = identifier == data['recommended_choice']
        if selected:
            recommended = choice
        links = ' '.join(f'<a href="#evidence-{ref}">{string(ref)}</a>' for ref in choice['evidence_ids'])
        visual = visualization(choice['visualization']) if version == 3 else ''
        badge = '<span class="badge">Recommended</span>' if selected else ''
        cards.append(f'<article class="choice-card" id="choice-{identifier}"><div class="eyebrow">Choice {len(ids)} · {string(identifier)}</div><h2>{string(choice["title"])}{badge}</h2><p>{string(choice["friction"])}</p>{visual}<p><strong>Benefit:</strong> {string(choice["benefit"])}</p><p><strong>First slice:</strong> {string(choice["first_slice"])}</p><p class="meta"><strong>Tradeoff:</strong> {string(choice["tradeoff"])}</p><p class="meta">{links}</p></article>')

    if recommended is None or covered != set(ids):
        raise ValueError('recommendation or evidence choice references are invalid')
    details = ''
    if stage == 'design':
        selected_id = data['selected_choice'] if version == 3 else data['recommended_choice']
        selected_choice = next((choice for choice in choices if choice['id'] == selected_id), None)
        if selected_choice is None:
            raise ValueError('selected_choice must reference an existing choice')
        details = '<p class="status">Selected: ' + string(selected_choice['title']) + '</p>' + detail_sections(data['design'], data['first_pr'], version)
    checks = data['checks']
    if not isinstance(checks, list) or not checks:
        raise ValueError('expected executed or proposed check records')
    check_rows = []
    for check in checks:
        fields(check, 'status description result')
        if check['status'] not in {'executed', 'proposed', 'not run'}:
            raise ValueError('unknown check status')
        check_rows.append(f'<li><strong>{string(check["status"])}</strong> — {string(check["description"])}<p class="meta">{string(check["result"])}</p></li>')
    recommendation = f'<article class="recommendation"><div class="eyebrow">Sol recommends</div><h2>{string(recommended["title"])}</h2><p>{metadata["recommendation_reason"]}</p></article>'
    choice_content = '<section id="choices"><h2>Choose a direction</h2>' + (f'<p>{string(reason)}</p>' if reason.strip() else '') + '<div class="choice-list">' + ''.join(cards) + '</div></section>'
    if stage == 'choices':
        next_step = '<section class="selection"><h2>Your choice comes next</h2><p>Reply in chat with a choice number or ID. Detailed redesign starts after your selection. Say “choose for me” to use the recommendation.</p></section>'
        content = recommendation + choice_content + next_step
        navigation = '<a href="#choices">Compare choices</a><a href="#support">Evidence</a>'
    else:
        content = recommendation + details + '<div class="support-block"><h3>Other choices considered</h3>' + choice_content + '</div>'
        navigation = '<a href="#design">Selected redesign</a><a href="#delivery">First PR</a><a href="#support">Evidence</a>'
    content += '<section id="support" class="support"><h2>Supporting detail</h2><div class="support-block"><h3>Source evidence and confidence</h3>' + ''.join(evidence_rows) + '</div><div class="support-block"><h3>Executed and proposed checks</h3><ul>' + ''.join(check_rows) + '</ul></div></section>'
    parts = {'TITLE': metadata['title'], 'META': f'{metadata["target"]} · {metadata["revision"]} · {metadata["date"]}', 'REPOSITORY': metadata['repository'], 'STATUS': metadata['evidence_status'], 'CONTENT': content, 'NAV': navigation}
    template = (SKILL / 'templates/proposal.html').read_text()
    document = re.sub(r'\{\{([A-Z_]+)\}\}', lambda match: parts[match[1]], template)
    if set(re.findall(r'\{\{([A-Z_]+)\}\}', template)) != set(parts):
        raise ValueError('template and renderer fields differ')
    handoff = '# ' + data['title'] + '\n\nCanonical technical content; generated from proposal.json.\n\n```json\n' + json.dumps(data, indent=2, ensure_ascii=False) + '\n```\n'
    return document, handoff


def atomic_write(path: Path, content: str) -> None:
    """Publish a complete artifact without replacing prior output on validation failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> None:
    """Generate an HTML report and human-readable technical archive, or validate only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('proposal', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('--check-sources', action='store_true', help='require existing source paths and valid line ranges')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    try:
        data = json.loads(args.proposal.read_text())
        document, handoff = render(data, args.check_sources)
        if not args.validate_only:
            output = args.output or args.proposal.with_name('report.html')
            if output.resolve() == args.proposal.resolve():
                raise ValueError('output must differ from proposal input')
            archive = output.with_name('handoff.md')
            if archive.resolve() in {output.resolve(), args.proposal.resolve()}:
                raise ValueError('report, input and handoff paths must differ')
            if archive.exists() and 'Canonical technical content; generated from proposal.json.' not in archive.read_text():
                raise ValueError('existing handoff is not generated; choose a fresh output directory')
            atomic_write(archive, handoff)
            atomic_write(output, document)
        print(f'Validated {len(data["choices"])} choices, {len(data["evidence"])} evidence entries; all structured fields rendered. Source ranges {"checked" if args.check_sources else "unchecked"}.')
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Render failed: {error}\n')


if __name__ == '__main__':
    main()
