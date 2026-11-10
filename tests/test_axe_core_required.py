"""The S016 browser accessibility audit must fail loudly when axe-core is absent.

QA G5 at 874c1f5 noted that tests/browser/s016.cjs logged "axe unavailable offline"
and continued when /tmp/cxui-axe (or AXE_CORE_PATH) was missing. There is no
existing skip/opt-out env-var pattern for this audit, so the helper has none.
"""
from __future__ import annotations

import os
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
