# SWEELAH-ISSUE-8-QA-NITS: low-priority G5 notes at 874c1f5 (Refs #8)

> **INTERNAL.** No production deploy. Phase 9 stays NO-GO. Status: **Implemented, unverified by QA (G5 pending on this conditions commit).** Not pushed.

- Branch: `fix/issue-8-qa-nits` (no upstream), worktree `/workspace/sweelah-issue-8-nits`
- **Base: `feat/issue-8-scenario-mapping-v2` @ `874c1f5e2ffd8eb7fc560d5c04ac7b2b42b3798c`**, parent `edf3caa435b56773816ca72d944e0bc7e5d0bcab`. Nits (2) and (3) live in #8 code that is not on `main` yet, so this is one branch covering all three, created with `git worktree add -b fix/issue-8-qa-nits … 874c1f5` (not from the frozen `/workspace/sweelah-issue-8-v2` worktree).
- `origin/main` is still `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (confirmed after fetch).
- Source of the nits (read-only): QA G5 verdict at `/workspace/qa-sweelah-issue-8-874c1f5/qa/issue-8-874c1f5/VERDICT.md` and `qa/issue-8-874c1f5-verify` @ `b9a5920`. `/workspace/sweelah-issue-8-v2` was not modified.
- This follow-up sits on `989bb8245ffce4b23f331c05014f3bdfb3af4ef2` and addresses the three non-blocking conditions in QA G5 at `/workspace/qa-sweelah-issue-8-989bb82/qa/issue-8-989bb82/VERDICT.md` (`qa/issue-8-989bb82-verify` @ `833def4`).

## 1. Nit (1) — axe audit no longer skips silently

The skip lived in `tests/browser/s016.cjs`, which is also on `main`. Two sites logged `axe unavailable offline` and continued when `AXE_CORE_PATH` was unset and `require.resolve('axe-core/axe.min.js')` failed: the shared `axe()` helper, and the `accessibility` case.

Both now call `requireAxeCorePath()` from the new `tests/browser/require_axe_core.cjs`. If the path is unset and the package is not resolvable, or if `AXE_CORE_PATH` points at a missing file, the helper throws a clear error and the browser case fails. There is **no opt-out env var**. The repo has no similar skip/allow pattern for this audit (the only browser skips are for missing Node/Playwright/Chromium, which make the whole suite impossible to run). Vendoring axe-core was not done here.

**“Fails loudly” covers only an absent or missing path**, not a directory or a broken file. An unset, empty or unresolvable path, or an `AXE_CORE_PATH` that does not exist, gets the guided helper error. A directory, an unreadable file, or a broken / non-axe file still fails, but with a raw Node or Playwright error (EISDIR, EACCES, TypeError, ReferenceError). That is unchanged from the parent and is not a silent skip. The helper only checks that the path exists; it does not validate that the file is readable axe-core.

**CI runs only the static check.** `.github/workflows/ci.yml` installs no Node, Playwright or axe, so the 46 browser cases and the helper subprocess tests (which call `_node()`) self-skip there. Only the source-string guards run in CI, including the silent-catch test added in this follow-up.

## 2. Nit (2) — dangling guardrail messages quote the offending text

In `retirepilot/scenario_mapping_internal.py`, `reference_errors()` now emits `{sid}: dangling guardrail {actual_guardrail!r}`. An invented string, an empty string, and a missing key are quoted as `'softened invented guardrail'`, `''`, and `None` respectively. A real guardrail copied from another scenario is still reported as `guardrail does not match research contract` (unchanged).

## 3. Nit (3) — `exits.txt` records the scope-pin runs

`test-artifacts/issue-8/exits.txt` now includes:

- `scope-pin red exit=1` (full issue-8 file: 1 failed, 77 passed; contract cases: 1 failed, 25 passed; see `semantic-scope-pin-red.log`)
- `targeted green exit=0` (78 passed; see `green-phase-targeted.log`)

Those lines describe the already-cited 874c1f5 runs. The historical logs were not rerun or rewritten.

## 4. Tests (test-first)

Red, on the unmodified 874c1f5 sources plus the new assertions: `red-phase.log`, **5 failed**.

- Four new tests in `tests/test_axe_core_required.py`: absent axe-core must fail loudly; a missing `AXE_CORE_PATH` must fail and name the path; an existing path must resolve; `s016.cjs` must use the helper and must not contain `axe unavailable offline`.
- `test_reference_checker_detects_mismatched_and_dangling_facts_and_guardrails` now requires the quoted invented text, and also locks in empty-string and missing-key quoting.

Green after the fix: `green-phase-targeted.log`, **5 passed**.

## 5. Full suites

Python 3.13.5, `/workspace/sweelah-baseline-venv`, 10 Nov 2026, 10:07–10:10pm SGT. Host previews on ports 8769–8773 were left running.

| Suite | Result | Log |
|---|---|---|
| `pytest -q -rs` (full), `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` | **903 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning (starlette/anyio). That is 899 at 874c1f5 + 4 new axe tests | `pytest.log` |
| Rules `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** (needs `PYTHONPATH=.`; without it the script raises ModuleNotFoundError, same as on main) | `rules.log`, `rules-no-pythonpath.log` |
| Browser `tests/test_s016_browser.py -v -s` (Chromium), same `AXE_CORE_PATH` | **46 passed**. `grep -c PASSED` = 46, `grep -cw PASS` = 47, `grep -c PASS` = 93 (46 `PASSED` + 46 `PASS S016 browser` + 1 `axe WCAG checks PASS`). Zero `axe unavailable` lines | `browser.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace; `PATH` includes the baseline venv so the script can spawn `python -m uvicorn`; host previews untouched) | **PASS 20/20** | `api.log` |
| Release `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

Exit codes: `exits.txt`. Environment: `env.txt`.

Browser runs also wrote PNGs and axe JSON under `test-artifacts/cxui-*` and `qa-*`. Those were not staged.

## 6. Visible UI change: **No**

No HTML, CSS, JS, API route or service code changed. The mapping module is still read-only metadata. **G5X should not be needed.**

## 7. Manifest pins (reported only; no manifest edited)

None of the files changed or added here are listed in `docs_release/RELEASE_MANIFEST_v2.7.json`, `docs_v26/VERIFICATION_MANIFEST_v26.json`, `docs/SOURCE_IMPORT_MANIFEST.json`, `docs_release/BINARY_DOCUMENT_MANIFEST_v2.7.json`, `design/sweelah/ASSET_MANIFEST.json`, or `research/retirepilot_2026_11_04/INTEGRITY_MANIFEST.json`.

File sha256 (content, not git blob):

| File | 874c1f5 | this commit |
|---|---|---|
| `tests/browser/s016.cjs` | `649a94e8d9087e6b7979a26508667eac028b4456c04a30275950291e2983ba76` | `73da1d972aac7ea7c67c66a94e9a3289b9ca157b20eff14f62ae9e25a02968e2` |
| `retirepilot/scenario_mapping_internal.py` | `a6711f87a1e13c80ad100c35a2edb983761c43bf1fb0cea5c9f8a6cdb1657627` | `71570a1542ff7a44fba814a11d9f9fc267a6064ffbb0aae26d3b7de308bf6d79` |
| `tests/test_scenario_mapping_internal_issue8.py` | `d479e2c6101d6c247a4e61d4e99b48daaacf03be46ebbae28d01777630abc545` | `5c2adce3324faf32463c7068d6494f16163064d3fa2d31b3601ca11d52042fb7` |
| `test-artifacts/issue-8/exits.txt` | `5630c57c9563121278c1161afea2d94203fdeb274d2b8bc58d7b093b9c6972b4` | `2f2f7a5b784f5bf888f7e5081d1fcc9a0f42197f39c999961831d1e55957e770` |

New, unpinned: `tests/browser/require_axe_core.cjs` (`2cea0a6d251771da8413118ba8270b5846af41fd104698d55eb1e16e40a3fad4`), `tests/test_axe_core_required.py` (`9539d7a7fbc2b90a55613a2b131b410153f1d652ea2a0a951cb74396f86c5e7c`), and `test-artifacts/issue-8-qa-nits/*`.

The pre-existing stale pins on other files (tracked under MANIFEST-PINS) were not touched.

## 8. Residual risks

- Browser accessibility cases will now fail in any environment that has neither `AXE_CORE_PATH` nor an installed `axe-core` package. That is the intended fix. This run used `/workspace/qa-tools/node_modules/axe-core/axe.min.js` (axe-core 4.14.0, sha256 `20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878`). That path is outside the repo and is not vendored.
- Quoting uses Python `repr()`, so a missing guardrail key is shown as `None` rather than a dedicated "missing key" phrase. The negative test locks that in.

## 9. QA G5 conditions on 989bb82

### README
`retirepilot/S016_README.md` (the paragraph that was lines 101–102 at 989bb82) no longer says the suite “explicitly reports the gap” when axe is missing. It now says the axe audit requires an offline `axe-core` package or `AXE_CORE_PATH` pointing at an existing `axe.min.js`, and that if that path is unset, unresolvable or missing, the audit fails instead of skipping or only reporting the gap.

### Silent-catch test (test-first)
`tests/test_axe_core_required.py` adds `test_require_axe_core_path_call_sites_are_not_wrapped_in_a_silent_catch`. It is a Node-free static check: there must be exactly two `requireAxeCorePath()` call sites in `tests/browser/s016.cjs`, and neither may sit inside a `try` whose `catch` swallows the error (`catch {}`, `catch {return;}`, or any catch that does not rethrow or set an exit). The existing `try/finally` around the browser session, and the launch `catch` that rethrows, are accepted.

QA’s mutants, applied one site at a time on a temp copy (the worktree `s016.cjs` was not left mutated):

| Mutant | Old targeted tests (82, as at 989bb82) | New test |
|---|---|---|
| Unmodified control | n/a | **1 passed** (`mutant-control-new-test.log`) |
| Site 1 (`axe()` helper): `try {axePath=requireAxeCorePath();} catch {return;}` | **82 passed — SURVIVES** (`mutant-site1-old-tests.log`) | **1 failed** at line 42 (`mutant-site1-new-test.log`) |
| Site 2 (`accessibility` case): `try {axePath=requireAxeCorePath();} catch {}` | **82 passed — SURVIVES** (`mutant-site2-old-tests.log`) | **1 failed** at line 704 (`mutant-site2-new-test.log`) |

Green on the real tree: `green-phase-targeted-g5c.log`, **83 passed** (78 issue-8 + 5 axe tests).

### Previous env.txt
The `env.txt` written for 989bb82 (`Tue Nov 10 22:10:51 +0800 2026`) **predated that commit** (`2026-11-10 22:14:34 +0800`) and recorded the base SHA `874c1f5e2ffd8eb7fc560d5c04ac7b2b42b3798c`, not the commit. It has been refreshed with this run, immediately before the conditions commit, and records parent `989bb8245ffce4b23f331c05014f3bdfb3af4ef2` and `AXE_CORE_PATH=/workspace/qa-tools/node_modules/axe-core/axe.min.js`.

## 10. Suites on this conditions commit

Python 3.13.5, `/workspace/sweelah-baseline-venv`, 14 Nov 2026, 10:22–10:24am SGT (UTC+8). Host ports 8769–8773 were not listening and were left untouched. Pytest (full) and the browser and API suites ran under `unshare -rn` with `ip link set lo up`.

| Suite | Result | Log |
|---|---|---|
| Targeted `tests/test_axe_core_required.py tests/test_scenario_mapping_internal_issue8.py` | **83 passed**, 0 failed, 0 skipped | `green-phase-targeted-g5c.log` |
| `pytest -q -rs` (full), `AXE_CORE_PATH=/workspace/qa-tools/node_modules/axe-core/axe.min.js` | **904 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning (starlette/anyio). That is 903 at 989bb82 + 1 new silent-catch test | `pytest-g5c.log` |
| Rules `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** (needs `PYTHONPATH=.`; without it the script raises ModuleNotFoundError, same as on main) | `rules-g5c.log`, `rules-no-pythonpath-g5c.log` |
| Browser `tests/test_s016_browser.py -v -s` (Chromium), same `AXE_CORE_PATH` | **46 passed**. `grep -c PASSED` = 46, `grep -cw PASS` = 47, `grep -c PASS` = 93 (46 `PASSED` + 46 `PASS S016 browser` + 1 `axe WCAG checks PASS`). Zero `axe unavailable` lines | `browser-g5c.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace; `PATH` includes the baseline venv; host ports untouched) | **PASS 20/20** | `api-g5c.log` |
| Release `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release-g5c.log` |
| Assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets-g5c.log` |

Exit codes: `exits.txt` (historical 989bb82 lines kept; this run appended). Environment: `env.txt`.

Browser runs also wrote PNGs and axe JSON under `test-artifacts/cxui-*` and `qa-*`. Those were not staged.

## 11. Manifest pins (reported only; no manifest edited)

None of the files changed or added in this follow-up are listed in the manifests named in §7. File sha256 (content, not git blob):

| File | 989bb82 | this commit |
|---|---|---|
| `retirepilot/S016_README.md` | `f2715e232f974fbb8b62b3e3e9ee10f56c6d28d99ae6c998773c3ca08775eb7d` | `620f40cec479d32718c1a2630312bee7fbf04dca34c828c518362ba9de2ed78e` |
| `tests/test_axe_core_required.py` | `9539d7a7fbc2b90a55613a2b131b410153f1d652ea2a0a951cb74396f86c5e7c` | `9294040771e480deb10c2de58e6585e72bb78291bf6e74729ab22cb9d4d58845` |

`tests/browser/s016.cjs` and `tests/browser/require_axe_core.cjs` are unchanged (`73da1d972aac7ea7c67c66a94e9a3289b9ca157b20eff14f62ae9e25a02968e2` and `2cea0a6d251771da8413118ba8270b5846af41fd104698d55eb1e16e40a3fad4`). New logs under `test-artifacts/issue-8-qa-nits/*-g5c.log` and `mutant-*.log` are unpinned. The pre-existing stale pins on other files were not touched.

Visible UI change: **No**. No HTML, CSS, JS, API route or service code changed in this follow-up. **G5X should not be needed.**
