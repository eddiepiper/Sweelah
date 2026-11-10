# SWEELAH-STAT-LEAPDOB — 29-Feb DOB ValueError in statutory_2026

**Ticket:** SWEELAH-STAT-LEAPDOB (CoS assignment under standing defect rule, 10 Nov 2026, Asia/Singapore)  
**Worktree:** `/workspace/sweelah-stat-leapdob`  
**Branch:** `fix/statutory-leap-dob` (no upstream; not pushed)  
**Parent:** `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (`origin/main`, confirmed)  
**Status:** Implemented but unverified. G5 at `e9b7509` was PASS with conditions; report wording was corrected at `cde5c9f`. This follow-up (`SWEELAH-LEAPDOB-YEARCAP`) is a new commit on top of `cde5c9f`. Do not push, amend, rebase, or open a PR.

## 1. Root cause

`retirepilot/statutory_2026.py::_band_index` built each age-band anniversary as:

```python
birthday = date(born.year + threshold, born.month, born.day)
```

For a synthetic 29-Feb date of birth this constructs `date(<year>, 2, 29)` whenever `born.year + threshold` is a common year, which raises `ValueError: day is out of range for month`.

The crash is not limited to the month of the birthday. `_band_index` always constructs every cutoff anniversary (employee: 55/60/65/70; platform: 35/45/50/55/60/65/70). Those anniversaries are five or more years apart, so at least one of them is always a common year. Every 29-Feb DOB therefore crashed `employee_ow_cpf` and `platform_cpf`, including mid-band months such as `employee_ow_cpf(dob='1972-02-29', month='2027-03', ...)`.

`self_employed_medisave_2026` already goes through `core.age_on`, which compares `(month, day)` tuples and does not construct an invalid date, so it did not crash.

## 2. Fix

Added `_attained_age_date(born, age)` and used it in `_band_index`. It returns `date(year, month, day)` when that calendar day exists, and **1 March** when 29 Feb does not exist in the target year.

This matches `core.age_on`: a 29-Feb person is still the younger age on 28 Feb of a common year and attains the new age on 1 Mar. Age-band changes continue to take effect in the month *after* the attained-age month, so:

- Common year (e.g. 1972-02-29 turning 55 on 2027-03-01): March keeps the prior band; April takes the next band.
- Leap year (e.g. 1968-02-29 turning 60 on 2028-02-29): February keeps the prior band; March takes the next band.

Money math is unchanged (still Decimal, same rounding helpers). The change is limited to anniversary date construction.

**INTERNAL ASSUMPTION, not checked against the CPF Board or any statutory convention (Phase 7 external review skipped):** treating 1 March as the attained-age date in a common year is aligned with the engine's existing `core.age_on` behaviour only. It is documented in the `_attained_age_date` docstring.

## 3. Other `date(year, dob.month, dob.day)`-style constructions in `retirepilot/`

| Location | Crash on 29-Feb? | Action |
|---|---|---|
| `statutory_2026._band_index` (the defect) | Yes | **Fixed** in this commit |
| `projection_v22._anniversary` | No — already clamps with `monthrange` to 28 Feb in a common year | **Not changed.** That clamp disagrees with `age_on` (boundary falls a day early). It is issue #9, already being fixed on a separate branch from main. Out of scope here. |
| `core.age_on` | No — tuple comparison `(month, day)` | Left unchanged; this is the convention the fix follows |
| `cpf_retirement_v26.transition_at_55` | No — compares `(today.month, today.day)` to the DOB. An "exact 55th-birthday" snapshot for a 29-Feb DOB is only possible when `as_of` itself is 29 Feb (so the 55th year must be a leap year). A common-year `as_of` of 1 Mar raises the existing `CPFUnsupportedCase`, not `ValueError`. | Listed, not changed |
| `policy.py` | **Yes (correction, QA G5 at e9b7509).** `policy.py:47` calls `statutory_2026._band_index` for the CPF employee reference, so a 29-Feb DOB crashed there with the same `ValueError`. Its own `dob.year + 55` arithmetic is integer-only and does not crash. | **Fixed by this commit** through `_band_index`; `policy.py` itself is unchanged |
| `date(year, month, 1)` / `monthrange` end-of-month constructions | No | Listed, not changed |

## 4. Red / green

Tests were written first in `tests/test_statutory_leap_dob.py` (synthetic 29-Feb DOBs only).

- **Red** (parent `823ef72` source + new tests): `red-phase.log`, **24 failed, 3 passed**. Every failure is `ValueError: day is out of range for month` at `statutory_2026.py:45`. The three passes are the `age_on` convention checks and `self_employed_medisave_2026`, which did not use `_band_index`.
- After the product fix, one agreement test still failed because it passed the employee cutoff list (`55/60/65/70`) for a age-50 platform birthday. That was a test error, not a product error; the cutoff list was corrected.
- **Green:** `green-phase.log`, **27 passed**, 0 failed.

The new tests cover: no-crash for employee and platform APIs across several 29-Feb cohorts; common-year transitions in April for 2026/2027 public APIs; leap-year transitions in March via `_band_index` (2024 and 2028, which the 2026/27 monetary APIs cannot query); and a sweep of all months in 2024–2028 (leap and common) for five synthetic 29-Feb DOBs.

## 5. Full suites

All runs used `/workspace/sweelah-baseline-venv` (Python 3.13.5) with `PYTHONPATH=.` in this worktree. Host previews on ports 8769–8773 were left running. No other worktree was checked out or edited.

| Suite | Result | Log |
|---|---|---|
| New tests, red | 24 failed, 3 passed | `red-phase.log` |
| New tests, green | **27 passed** | `green-phase.log` |
| `pytest -q -rs --ignore=tests/test_s016_browser.py` | **802 passed**, 0 failed, 1 dependency deprecation warning | `pytest.log` |
| Browser `tests/test_s016_browser.py -q -s` with `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` (real Chromium 156.0.8078.47) | **46 passed**; `axe WCAG checks PASS` | `browser.log` |
| Combined pytest + browser | **848 passed** (821 on main + 27 new) | — |
| Rule contracts `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` | **PASS 20/20**, run under `unshare -rn` with loopback up (its own :8769 inside the namespace; host previews 8769–8773 untouched) | `api.log` |
| Release documents `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Design assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

## 6. Visible UI output change: **Yes** for 29-Feb profiles; **No** for shipped samples

`service.evaluate()` for all three bundled households (`data/*household*.json`) is **byte-identical** to `origin/main`'s `statutory_2026.py`. None of those profiles has a 29-Feb DOB (`ui-compare.log`). Default UI chart text and "Baseline projected accessible assets" do not change. Labels and copy are unchanged.

**Correction (QA G5 at e9b7509): the visible fix.** On main `823ef72`, any household where a person with a 29-Feb DOB reaches the CPF employee reference path makes `service.evaluate` raise `ValueError: day is out of range for month`. That path is a Singapore citizen, or a PR in CPF year 3 or later, with `as_of` in 2026 or 2027. The UI and `POST /api/evaluate` then return **422**. On this branch the same households return **200** with a full evaluation. I checked this by setting every person's DOB to `1972-02-29` in the bundled `retired_household` and `salaried_household`:
- SG and PR: 422/`ValueError` on main, success on this branch.
- Foreign residents: success on both, because they do not reach `_band_index`.

So every 29-Feb user on that path goes from an error to a result. That is a user-visible change, although no labels, copy or layout change.

Previous wording, kept for history: for a synthetic profile with a 29-Feb DOB, `employee_ow_cpf` / `platform_cpf` / `cpf_contribution_review` previously raised `ValueError` and would now return a bounded reference (and, in a common-year attained-age month, keep the prior band through March). Cash-flow and projection still use user-supplied deductions, not these statutory references, so the default forecast chart is unaffected unless a later path starts displaying the reference amounts. Recommendation: G5X is not required for shipped content; CoS to decide whether the newly-non-crashing 29-Feb statutory reference counts as a visible change.

## 6a. Merge-order requirement: land together with #9

This branch must land **back to back with #9** (`fix/issue-9-partial-month`), **with no release in between**. Merge order: STAT-LEAPDOB first, then #9. On its own, this branch makes statutory references use the 1-Mar convention, while `projection_v22._anniversary` on main still uses 28 Feb. The two conventions would be mixed in one evaluation. #9 aligns the projection to 1 Mar. Manifest-pin updates for both branches may be needed after SWEELAH-MANIFEST-PINS lands; that report will list them.

## 7. Residual risks

1. **Leap-day convention is an internal assumption.** 1 March in a common year follows `core.age_on` only. It has not been checked against the CPF Board or any statutory payroll convention. Phase 7 (external review) is skipped.
2. **`projection_v22._anniversary` is still wrong on this branch** (clamps to 28 Feb). That is issue #9, fixed separately on `fix/issue-9-partial-month`; it was not merged into this worktree, by design.
3. **`transition_at_55` still requires an exact calendar match** of `(month, day)`. A 29-Feb member has no exact 55th-birthday snapshot in a common year; callers still get `CPFUnsupportedCase`. That is existing bounded-reference behaviour, not this crash.
4. Supported employee/platform monetary years remain 2026/2027 (both common years). Leap-year *transition month* behaviour is unit-tested via `_band_index` for 2024 and 2028, not through those monetary APIs.

## 8. Constraints observed

No push, PR, merge, force-push or amend. Synthetic dates only; no NRIC, CPF account, bank or real user data; no secrets; no paid services or deploys; no Supermemory or connectors. Existing named worktrees (including `sweelah-issue-8`, `sweelah-issue-9`, `sweelah-cxui-*`, `sweelah-qa-*`, `/workspace/sweelah`, `eng-onb-*`) were left untouched. Previews on 8769–8773 were not stopped. No preview was required on 8776.

## 9. Follow-up: SWEELAH-LEAPDOB-YEARCAP (QA G5 condition, 10 Nov 2026)

The same helper overflow QA found on CPF55 exists here. `_attained_age_date` raised a bare `ValueError: year 10000 is out of range` when `born.year + age` exceeds 9999, because the 29-Feb fallback `except ValueError` also constructs a date in that year. A 29-Feb DOB near the limit, for example `9944-02-29` at age 56, hit the same path.

**Fix.** The helper now checks the target year against `date.min.year` / `date.max.year` (1–9999) before constructing a date, and raises `core.ValidationError` with a clear message: `Attained-age calendar year is outside the supported date range (1-9999)`. The 29-Feb → 1-Mar fallback is unchanged for in-range years.

**Why `ValidationError`.** `statutory_2026` has no `CPFUnsupportedCase` (that type lives in `cpf_retirement_v26`). Unsupported monetary cases in this module usually return a `_blocked` dict (`status: requires_review`), but `_attained_age_date` must return a `date` and `_band_index` must return an int, so a dict cannot be used at the helper. `core.ValidationError` is the engine's existing validation / unsupported-input exception.

**HTTP and parent behaviour.** The only HTTP path that can reach this guard is `POST /api/reference` with `kind=employee_cpf_schedule` (`employee_ow_cpf` → `_band_index` → `_attained_age_date`), which takes a caller-supplied `dob` and does not apply the profile `as_of` future-DOB check. `POST /api/evaluate` cannot reach the guard: `core.validate` rejects a date of birth after `as_of`, and both `policy_reference` and `review_household_contributions` only invoke `_band_index` when the period year is 2026 or 2027, which would make a 9945+ DOB a future date of birth. The `/api/reference` handler already mapped `ValueError` to HTTP 422 on the parent (`cde5c9f`). A year overflow therefore already returned 422 with the bare message `year N is out of range`, not a 500. The year-cap fix only changes that message to the controlled `ValidationError` text.

**Impossible dates.** An impossible date such as `9945-02-29` (9945 is not a leap year) still raises a bare `ValueError: day is out of range for month` from `date.fromisoformat` in `_band_index`, before the year-cap guard runs. That `ValueError` also maps to HTTP 422. This behaviour is unchanged.

**Helper copy.** This `_attained_age_date` and the copy in CPF55 (`retirepilot/cpf_retirement_v26.py` on `fix/cpf55-leap-dob`) are verbatim copies of each other, apart from the exception type (`ValidationError` here, `CPFUnsupportedCase` there).

**Manifests.** `docs/SOURCE_IMPORT_MANIFEST.json` and `docs_release/RELEASE_MANIFEST_v2.7.json` still pin `retirepilot/statutory_2026.py` at sha256 `8bee6239…`. The pin is stale relative to this branch (current sha256 `5075d5b4…`). That is handled by the SWEELAH-MANIFEST-PINS ledger refresh after the leap set lands; this commit does not touch manifests.

**Tests** (written first) in `tests/test_statutory_leap_dob.py`:
- `9950-01-15` at age 55 (year 10005) and the leap-day DOB `9944-02-29` at age 56 (year 10000) raise `ValidationError`, not a bare `ValueError`, both on the helper and via `_band_index` (the public-path leap-day case is `9948-02-29`).
- `9944-02-29` at age 55, the last in-range 29-Feb / age-55 anniversary, still returns `9999-03-01`.

Red: `yearcap-red.log`, **2 failed, 28 passed**. Both failures are `ValueError: year 10005 is out of range` from the helper. Green: `yearcap-green.log`, **30 passed**.

### Suites re-run on this commit

All runs used `/workspace/sweelah-baseline-venv` (Python 3.13.5) with `PYTHONPATH=.` in this worktree. Host previews on ports 8769–8773 were left running.

| Suite | Result | Log |
|---|---|---|
| Year-cap tests, red | 2 failed, 28 passed | `yearcap-red.log` |
| Year-cap tests, green | **30 passed** | `yearcap-green.log` |
| `pytest -q -rs --ignore=tests/test_s016_browser.py` | **805 passed**, 0 failed, 1 dependency deprecation warning | `pytest.log` |
| Browser `tests/test_s016_browser.py -q -s` with `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` (real Chromium 156.0.8078.47) | **46 passed**; `axe WCAG checks PASS` | `browser.log` |
| Combined pytest + browser | **851 passed** (821 on main + 30 on this branch) | — |
| Rule contracts `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` | **PASS 20/20**, run under `unshare -rn` with loopback up (its own :8769 inside the namespace; host previews 8769–8773 untouched) | `api.log` |
| Release documents `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Design assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |
