# SWEELAH-API-REF-KEY: unknown /api/reference key returns 422 not 500

> **INTERNAL — NOT EXTERNALLY REVIEWED OR SIGNED OFF.** Synthetic data only. Phase 9 stays NO-GO.

- Status: **Implemented but unverified.** QA G5 of `4bbe97c` was **PASS with conditions** (`/workspace/qa-sweelah-api-ref-key/qa/api-ref-key-4bbe97c/VERDICT.md`, QA branch `qa/api-ref-key-4bbe97c-verify` @ `41d6177`). This commit addresses the report conditions only. Not pushed.
- Branch: `fix/api-reference-bad-key` (no upstream), worktree `/workspace/sweelah-api-ref-key`.
- Base: main `5fe3ec8b6448d94d4a15dc18f1f38c2a58508e76` (confirmed after `git fetch origin`). Code remains `4bbe97c0609ba25d9f36ae8bf2878dadd6305cfe`.
- Environment: `env.txt`. Exit codes: `exits.txt`.

## 1. Repro (main 5fe3ec8, `POST /api/reference`, synthetic `RP-SYNTH-001`)

A valid request (`kind=resident_tax` with confirmed YA 2026 chargeable income 120000) returns 200 and `tax_before_rebates_sgd=7950.00`. The following inputs did not:

| Input | Status on 5fe3ec8 | Detail on 5fe3ec8 |
|---|---|---|
| unknown `kind` (probe string) | 422 | `Unsupported reference calculation` (controlled; already correct) |
| missing `kind` | 422 | same |
| empty-string `kind` | 422 | same |
| `kind` as a list or object | **500** Internal Server Error | uncaught `TypeError: unhashable type` |
| non-object body (`[]`, `"hello"`, `null`, `1`, `true`) | **500** | uncaught `AttributeError` on `data.get` |
| missing `month` / only an unknown key in an `employee_cpf_schedule` item | **500** | uncaught `KeyError` |
| unexpected or empty-string key in `params` | 422 | echoed the submitted key and internal name: `resident_tax_reference() got an unexpected keyword argument 'LEAK-ME-KEY-…'` |
| missing required `params` keys | 422 | leaked the internal function name and argument list |
| bad `dob` (e.g. `"QA-NOT-A-DATE"`) | 422 | echoed the submitted value: `Invalid isoformat string: 'QA-NOT-A-DATE'` |
| non-integer `pr_cpf_year` (e.g. `"QA-NOTINT"`) | 422 | echoed the submitted value: `invalid literal for int() with base 10: 'QA-NOTINT'` |
| `params` not an object | 422 | `params must be object` (already correct) |
| unknown CPF account key `XX` | 422 | `Invalid CPF account list` (already correct) |

## 2. Root cause

`reference_calculation` in `retirepilot/api.py` already rejected an unknown string `kind` and a non-object `params` with a controlled 422, but three 500 paths were open:

1. `if kind not in REFERENCE_FUNCTIONS` is evaluated before the `try/except`. A list or object `kind` is unhashable, so this raises `TypeError` and FastAPI returns 500.
2. A JSON body that is not an object (`[]`, a string, `null`, a number, `true`) has no `.get`, so `data.get('synthetic_profile_id', …)` raises `AttributeError` (also uncaught).
3. The `try/except` around `REFERENCE_FUNCTIONS[kind](**params)` caught only `ValueError` and `TypeError`. `employee_cpf_schedule_2026_27` does `item['month']` / `item['ordinary_wages']`, so a missing or wrong item key is a `KeyError` and became 500.

The `TypeError` path for an unexpected `params` key already returned 422, but `raise HTTPException(422, str(exc))` echoed arbitrary input and the internal function name.

## 3. Fix (`retirepilot/api.py`, `/api/reference` only)

Minimal, local to this handler. `body_json` is unchanged (that is the D-1/D-2 surface).

- Refuse a non-object body with 422 `request must be an object` (same wording as `/api/scenarios/S016/preview`) before any `.get`.
- Require `kind` to be a `str` and a known reference name; otherwise 422 `Unsupported reference calculation` (list, object, missing, empty string, unknown string).
- Catch `ValidationError` separately and keep its existing controlled messages (e.g. `Invalid CPF account list`).
- Catch remaining `ValueError`, `TypeError` and `KeyError` as 422 `Invalid reference parameters`. The submitted key and the internal function name are not echoed.

That generic branch also closes value echoes that were not listed in the first report. On `5fe3ec8`, a bad `dob` such as `"QA-NOT-A-DATE"` returned `Invalid isoformat string: 'QA-NOT-A-DATE'`, and a non-integer `pr_cpf_year` such as `"QA-NOTINT"` returned `invalid literal for int() with base 10: 'QA-NOTINT'`. Both are now the same fixed `Invalid reference parameters` message, with the submitted value absent from the body. The same path also covers an unhashable item `month` and a 5000-digit integer, which previously leaked Python's own text. QA confirmed these on a 190-case fuzz run. Existing `ValidationError` details are unchanged (35/35 byte-identical).

The Chief of Staff has decided to keep the fixed `Invalid reference parameters` message exactly as it is. That decision is **reported by an agent** and has not been independently verified from the repository; what the commit itself shows is that no per-kind allowed-keys message was added. A proposed follow-up that would list the allowed keys for each `kind` (still without echoing user input) was **not** made.

`require_synthetic_fixture` still runs before `kind`/`params` checks, so a missing or non-synthetic profile id remains 403.

## 4. Tests (test-first)

New file `tests/test_api_reference_bad_key.py` (18 cases, TestClient, `raise_server_exceptions=False`). Covers unknown `kind`, missing `kind`, empty-string `kind`, `kind` list/object, unknown and empty-string `params` keys (assert the probe key and `resident_tax_reference` / `employee_cpf_schedule` are absent from the body), missing required `params`, missing/unknown keys in schedule items, non-object bodies, unchanged `params`-must-be-object and `Invalid CPF account list` messages, and the valid resident-tax 200.

| Phase | Result | Log |
|---|---|---|
| **Red** (unmodified 5fe3ec8 `api.py`) | **12 failed, 6 passed**. The 12: `kind` list/object (500); unexpected/empty `params` key and missing required `params` (422 but leaked names/keys); missing/unknown schedule item keys (500); five non-object bodies (500). The 6 that passed are the already-correct cases. | `red-phase.log` |
| **Green** | **18 passed** | `green-phase.log` |

**Mutation spot-check** (`mutation.log`; each mutant applied alone, then `api.py` restored and verified byte-identical):

| Mutant | Result |
|---|---|
| M1 drop `isinstance(kind, str)` guard | 2 failed (`kind` list/object) |
| M2 drop `KeyError` from `except` | 2 failed (schedule item keys) |
| M3 echo `str(exc)` instead of the controlled params message | 5 failed (unexpected/empty/missing `params`, plus both schedule cases) |
| M4 drop `isinstance(data, dict)` check | 5 failed (non-object bodies) |
| M5 revert `reference_calculation` to 5fe3ec8 | 12 failed, 6 passed (matches red) |

## 5. Full suites (Python 3.13.5, `/workspace/sweelah-baseline-venv`)

| Suite | Result | Log |
|---|---|---|
| `pytest -q -rs` (full) | **1008 passed**, 0 failed (990 on main `5fe3ec8` + 18 new), 1 third-party DeprecationWarning | `pytest.log` |
| Rule contracts (`PYTHONPATH=.`) | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace, `ip link set lo up`; host ports 8769-8773 untouched) | **PASS 20/20** | `api.log` |
| Browser `tests/test_s016_browser.py -v -s` under `unshare -rn` (chromium-1254, `AXE_CORE_PATH=/workspace/qa-tools/node_modules/axe-core/axe.min.js`) | **46 passed**, `axe WCAG checks PASS` | `browser.log` |
| Release `scripts/verify_release_documents.py` | **9 artifacts, errors=0** | `release.log` |
| Assets `design/sweelah/verify_assets.py` | **6 HTML, 15 assets, 21/21** | `assets.log` |

The pytest, rules and API rows above are from the original run at `4bbe97c`. They were not rerun at the report-only follow-up `e75e950`, because the product was byte-identical; QA treated rules and API as Implemented but unverified at that commit. Browser, release and assets were cited in the `e75e950` conditions commit and rerun by QA.

## 6. Pinned files: sha256 before → after (reported only; no manifest edited)

| File | 5fe3ec8 (before) | This branch (after) | Pins |
|---|---|---|---|
| `retirepilot/api.py` | `48a5d5598e37b3101f8bf0a4c161ad079209d6ca31aae1e8bcac98a86f1d1446` (8464 bytes) | `711686572aef3143d211c868f85a4377e1240fd304fc48e0fe6021effd45e0f6` (8679 bytes) | `docs_release/RELEASE_MANIFEST_v2.7.json` pins `5198860114f6769ea7c0aee97f66a45b911a5d7c8636af82c0785f470df9419b` (already ≠ main); `docs/SOURCE_IMPORT_MANIFEST.json` pins `d4739b794d1589091fe6a04bbf7de022168b6cbd10a2e9c347fc2f4f10b71e65` (historical, ≠ main) |

No other pinned file changed. The ledger is not refreshed on this branch.

**Correction (QA G5 condition on §6):** `api.py` was **not** already in the pending ledger-refresh *add* list (that list at `fix/manifest-pins` @ 22bb38f is statutory, projection, cpf_retirement_v26, core, assistant). The 22bb38f ledger already has a `retirepilot/api.py` entry whose `current_sha256` is `48a5d5598e37b3101f8bf0a4c161ad079209d6ca31aae1e8bcac98a86f1d1446` (main `5fe3ec8`). That existing entry needs updating to `711686572aef3143d211c868f85a4377e1240fd304fc48e0fe6021effd45e0f6`. If D-1/D-2 `2fc5a03` also lands, the final merged `api.py` hash is provisionally `3289a45204839839ec996cacfcde765298afd43a92b8dce5a72b361c75c1c6aa`. The merge-tree `dd4cc32e` belongs to `4bbe97c`+`2fc5a03`; the tree for `e75e950`+`2fc5a03` is `ea0faa5d`. With the later D-1/D-2 tip `5e9933b` the tree is `24e5b52b`. The `api.py` hash `3289a452…` is the same in all three; the refresh should use the hash of the landed tree.

## 7. Overlap with D-1/D-2 branch `2fc5a03`

Both branches edit `retirepilot/api.py`. The surfaces do **not** overlap in the file:

- This branch changes only `reference_calculation` (the `/api/reference` handler). `body_json` is untouched.
- `2fc5a03` (`fix/error-clears-results-nonfinite`) changes `body_json` (non-finite number refusal) and the S016 `allow_nonfinite=True` call. It does not touch `reference_calculation`.

`git merge-tree --write-tree --messages` of this branch against `2fc5a03` (merge-base `5fe3ec8`) completed with **exit 0** and `Auto-merging retirepilot/api.py`. No conflict markers. The merged `api.py` contains both D-2's `body_json` non-finite check (including the S016 `allow_nonfinite=True` call) and this handler's 422 guards (`isinstance(data, dict)`, `isinstance(kind, str)`, `KeyError` → `Invalid reference parameters`). The branches can land in either order without a text conflict; QA should still re-check `/api/reference` after both are applied, because D-2's central `body_json` change is on the same request path.

## 8. Residual risks / not done

**Residual pre-existing 500s on `/api/reference` itself** (QA G5 condition 1; identical on parent `5fe3ec8`, so not a regression, and **not fixed here**):

- 7 cases at about `1e26` and above (the `'1e40'`-scale label understated the threshold): `chargeable_income` `"1e100"`, the JSON number `1e30`, and a 30-digit numeric **string** (`"1"+"0"*29`); `sale_price` `"1e40"` and `"1e999999999"`; OA balance `"1e40"`; wages `"1e40"`. `1e30` and the 30-digit string already return 500. These raise `decimal.InvalidOperation` in `money().quantize` or `decimal.Overflow`. Those are `ArithmeticError` subclasses, so they are not caught by `(ValueError, TypeError, KeyError)`.
- 1 case: a JSON body nested 50,000 deep (`[` repeated) hits `RecursionError` in `json.loads` inside `body_json`.

A proposed fix is on `fix/input-validation-polish` (C), under QA, and is not on this branch. That branch (`ec93254`) claims 422 for all 8; that claim is **Proposed / Implemented but unverified** until QA confirms it. These are candidates for the same input-polish D-3 work noted in the D-1/D-2 verdict (finite but huge numbers / overflow on the evaluate path).

- Other routes (`/api/evaluate`, `/api/ask`, `/api/guide`) still 500 on a non-object JSON body (`data.get` / `data['profile']`). Out of scope here; `/api/reference` only.
- TypeError/ValueError details from those other routes may still echo Python messages via `str(exc)`.
- Not run: CI (not pushed), Safari, screen reader, Python 3.11 CI, `tests/smoke_browser.py`. Firefox is not applicable to this API-only change.
