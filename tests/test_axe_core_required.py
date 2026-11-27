"""The S016 browser accessibility audit must fail loudly when axe-core is absent.

QA G5 at 874c1f5 noted that tests/browser/s016.cjs logged "axe unavailable offline"
and continued when /tmp/cxui-axe (or AXE_CORE_PATH) was missing. There is no
existing skip/opt-out env-var pattern for this audit, so the helper has none.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'tests/browser/require_axe_core.cjs'
BROWSER_SCRIPT = ROOT / 'tests/browser/s016.cjs'


def _node() -> str:
    node = shutil.which('node')
    if not node:
        pytest.skip('node is required to exercise the axe-core helper; no download attempted')
    return node


def _env_without_axe_path() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key != 'AXE_CORE_PATH'}
    env['NODE_PATH'] = ''
    return env


def _run_helper(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_node(), str(HELPER)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def test_axe_audit_fails_loudly_when_axe_core_is_absent():
    # The package is not part of this repo; confirm it is not resolvable here so
    # the test is exercising the missing-tool path, not a local install.
    probe = subprocess.run(
        [_node(), '-e', "require.resolve('axe-core/axe.min.js')"],
        cwd=ROOT,
        env=_env_without_axe_path(),
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        pytest.skip('axe-core is resolvable in this environment; cannot exercise the absent path')

    result = _run_helper(_env_without_axe_path())
    message = (result.stderr or result.stdout).strip()
    assert result.returncode != 0, message
    assert 'axe-core is required' in message
    assert 'AXE_CORE_PATH' in message
    assert 'silently' in message.lower() or 'will not be skipped' in message.lower()
    assert 'axe unavailable offline' not in message


def test_axe_audit_fails_loudly_when_axe_core_path_is_missing(tmp_path):
    missing = tmp_path / 'missing-axe.min.js'
    env = _env_without_axe_path()
    env['AXE_CORE_PATH'] = str(missing)
    result = _run_helper(env)
    message = (result.stderr or result.stdout).strip()
    assert result.returncode != 0, message
    assert 'AXE_CORE_PATH' in message
    assert 'does not exist' in message
    assert str(missing) in message


def test_axe_audit_resolves_an_existing_axe_core_path(tmp_path):
    present = tmp_path / 'axe.min.js'
    present.write_text('/* test fixture, not axe-core */\n')
    env = _env_without_axe_path()
    env['AXE_CORE_PATH'] = str(present)
    result = _run_helper(env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == str(present)


def test_s016_browser_script_does_not_skip_axe_silently():
    source = BROWSER_SCRIPT.read_text()
    assert "require('./require_axe_core.cjs')" in source
    assert 'axe unavailable offline' not in source

def _is_js_ident(ch: str) -> bool:
    return ch.isalnum() or ch in '_$'


def _js_keyword_at(source: str, index: int, word: str) -> bool:
    if not source.startswith(word, index):
        return False
    if index and _is_js_ident(source[index - 1]):
        return False
    end = index + len(word)
    if end < len(source) and _is_js_ident(source[end]):
        return False
    return True


def _skip_js_string(source: str, index: int) -> int:
    quote = source[index]
    index += 1
    length = len(source)
    if quote in ('"', "'"):
        while index < length:
            if source[index] == '\\':
                index += 2
                continue
            if source[index] == quote:
                return index + 1
            index += 1
        return length
    if quote != '`':
        return index
    while index < length:
        if source[index] == '\\':
            index += 2
            continue
        if source.startswith('${', index):
            index = _skip_js_template_expr(source, index)
            continue
        if source[index] == '`':
            return index + 1
        index += 1
    return length


def _skip_js_template_expr(source: str, index: int) -> int:
    index += 2
    depth = 1
    length = len(source)
    while index < length and depth:
        if source[index] in ('"', "'", '`'):
            index = _skip_js_string(source, index)
            continue
        if source.startswith('//', index):
            newline = source.find('\n', index)
            index = length if newline < 0 else newline + 1
            continue
        if source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = length if end < 0 else end + 2
            continue
        if source[index] == '{':
            depth += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return length


def _skip_js_ws_and_comments(source: str, index: int) -> int:
    length = len(source)
    while index < length:
        if source[index] in ' \t\r\n':
            index += 1
            continue
        if source.startswith('//', index):
            newline = source.find('\n', index)
            index = length if newline < 0 else newline + 1
            continue
        if source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = length if end < 0 else end + 2
            continue
        break
    return index


def _match_js_balanced(source: str, index: int, opener: str, closer: str) -> int:
    if index >= len(source) or source[index] != opener:
        raise ValueError(f'expected {opener!r} at {index}')
    depth = 0
    length = len(source)
    while index < length:
        char = source[index]
        if char in ('"', "'", '`'):
            index = _skip_js_string(source, index)
            continue
        if source.startswith('//', index):
            newline = source.find('\n', index)
            index = length if newline < 0 else newline + 1
            continue
        if source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = length if end < 0 else end + 2
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError(f'unbalanced {opener}{closer}')


def _try_catch_ranges(source: str) -> list[tuple[int, int, int, int]]:
    """Body offsets of every try { ... } catch { ... } in source."""
    ranges: list[tuple[int, int, int, int]] = []
    index = 0
    length = len(source)
    while index < length:
        if source[index] in ('"', "'", '`'):
            index = _skip_js_string(source, index)
            continue
        if source.startswith('//', index):
            newline = source.find('\n', index)
            index = length if newline < 0 else newline + 1
            continue
        if source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = length if end < 0 else end + 2
            continue
        if _js_keyword_at(source, index, 'try'):
            cursor = _skip_js_ws_and_comments(source, index + 3)
            if cursor < length and source[cursor] == '{':
                try_start = cursor + 1
                after_try = _match_js_balanced(source, cursor, '{', '}')
                cursor = _skip_js_ws_and_comments(source, after_try)
                if _js_keyword_at(source, cursor, 'catch'):
                    cursor = _skip_js_ws_and_comments(source, cursor + 5)
                    if cursor < length and source[cursor] == '(':
                        cursor = _match_js_balanced(source, cursor, '(', ')')
                        cursor = _skip_js_ws_and_comments(source, cursor)
                    if cursor < length and source[cursor] == '{':
                        catch_start = cursor + 1
                        after_catch = _match_js_balanced(source, cursor, '{', '}')
                        ranges.append((try_start, after_try - 1, catch_start, after_catch - 1))
            index += 3
            continue
        index += 1
    return ranges


def _strip_js_comments(source: str) -> str:
    parts: list[str] = []
    index = 0
    length = len(source)
    while index < length:
        if source[index] in ('"', "'", '`'):
            end = _skip_js_string(source, index)
            parts.append(source[index:end])
            index = end
            continue
        if source.startswith('//', index):
            newline = source.find('\n', index)
            index = length if newline < 0 else newline + 1
            continue
        if source.startswith('/*', index):
            end = source.find('*/', index + 2)
            index = length if end < 0 else end + 2
            continue
        parts.append(source[index])
        index += 1
    return ''.join(parts)


def _catch_is_silent(source: str, start: int, end: int) -> bool:
    text = ' '.join(_strip_js_comments(source[start:end]).split())
    if text in {'', 'return', 'return;'}:
        return True
    if re.search(r'\bthrow\b', text) or 'process.exit' in text or 'exitCode' in text:
        return False
    return True


def test_require_axe_core_path_call_sites_are_not_wrapped_in_a_silent_catch():
    # Static, Node-free: CI has no Node/Playwright/axe, so only this class of
    # check (and the existing source-string guard) runs there.
    source = BROWSER_SCRIPT.read_text()
    calls = list(re.finditer(r'(?<![\w$])requireAxeCorePath\s*\(', source))
    assert len(calls) == 2, (
        f'expected 2 requireAxeCorePath() call sites in {BROWSER_SCRIPT.name}, '
        f'found {len(calls)}'
    )
    silent: list[int] = []
    ranges = _try_catch_ranges(source)
    for match in calls:
        position = match.start()
        for try_start, try_end, catch_start, catch_end in ranges:
            if try_start <= position < try_end and _catch_is_silent(source, catch_start, catch_end):
                silent.append(source.count('\n', 0, position) + 1)
                break
    assert not silent, (
        'requireAxeCorePath() is wrapped in a silent try/catch at line(s) '
        + ', '.join(str(line) for line in silent)
        + '; the accessibility audit must fail, not skip, when axe-core is absent'
    )
