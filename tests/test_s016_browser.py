"""Real localhost browser checks, automatically collected by the CI pytest suite.

No installs or downloads: skip clearly if optional Node Playwright/Chromium absent.
"""
import glob
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def browser_server():
    node = shutil.which('node')
    if not node:
        pytest.skip('S016 browser checks need offline Node and Playwright; no download attempted')
    modules = [os.environ.get('PLAYWRIGHT_MODULE', 'playwright')]
    modules += glob.glob(str(Path.home() / '.npm/_npx/*/node_modules/playwright'))
    module = None
    for candidate in modules:
        probe = subprocess.run([node, '-e', 'require(process.argv[1])', candidate], capture_output=True)
        if probe.returncode == 0:
            module = candidate
            break
    if not module:
        pytest.skip('S016 browser checks need installed Node Playwright (PLAYWRIGHT_MODULE); no download attempted')
    browsers = [os.environ.get('S016_CHROMIUM', ''), shutil.which('chromium'), shutil.which('google-chrome')]
    browsers += glob.glob(str(Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))
    executable = next((p for p in browsers if p and Path(p).is_file()), '')
    # Playwright can also use its own default cached browser.
    env = dict(os.environ, PLAYWRIGHT_MODULE=module, S016_CHROMIUM=executable)
    probe = subprocess.run([node, str(ROOT / 'tests/browser/s016.cjs'), 'probe'], env=env, capture_output=True, text=True)
    if probe.returncode == 77:
        pytest.skip(probe.stderr.strip())
    assert probe.returncode == 0, probe.stdout + probe.stderr
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'retirepilot.api:app',
        '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{port}'
    try:
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail('Local S016 server exited before readiness')
            try:
                urllib.request.urlopen(base + '/api/sample', timeout=1).close()
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(.05)
        else:
            pytest.fail('Local S016 server failed readiness')
        yield node, env, base
    finally:
        process.terminate()
        process.wait(timeout=5)


@pytest.mark.parametrize('case', ['success', 'errors', 'server-refusal', 'nonmutation', 'mobile', 'accessibility', 'precision', 'mobile375', *['cxui-d%02d' % i for i in range(1, 12)], 'cxui-mapping', 'cxui-mobile375',
    'cxuifu-rd01', 'cxuifu-rd01-375', 'cxuifu-rd02', 'cxuifu-rd02-375', 'cxuifu-rd03', 'cxuifu-rd03-375',
    'cxuifu-exponent', 'cxuifu-wording',
    'cxuifu2-months', 'cxuifu2-months-375', 'cxuifu2-heading', 'cxuifu2-heading-375'])
def test_s016_real_browser(browser_server, case):
    node, env, base = browser_server
    result = subprocess.run([node, str(ROOT / 'tests/browser/s016.cjs'), case, base],
                            env=env, cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout)
