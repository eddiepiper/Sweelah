# SWEELAH-CPF55-LEAPDOB — 29-Feb DOB refused by transition_at_55

**Ticket:** SWEELAH-CPF55-LEAPDOB (CoS assignment under standing defect rule, 10 Nov 2026, Asia/Singapore)  
**Worktree:** `/workspace/sweelah-cpf55-leapdob`  
**Branch:** `fix/cpf55-leap-dob` (no upstream; not pushed)  
**Parent:** `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (`origin/main`, confirmed)  
**Status:** Implemented but unverified. G5 at `5452a46` was PASS with conditions; this follow-up (`SWEELAH-LEAPDOB-YEARCAP`) is a new commit on top of that tip. Do not push, amend, rebase, or open a PR.

## 1. Root cause

`retirepilot/cpf_retirement_v26.py::transition_at_55` accepted a snapshot only when the calendar year-difference was 55 and `(as_of.month, as_of.day)` exactly equalled `(dob.month, dob.day)`:

```python
if (today.year-birthday.year)!=55 or (today.month,today.day)!=(birthday.month,birthday.day):
    raise CPFUnsupportedCase('Only an exact 55th-birthday snapshot is supported; ...')
```

`core.age_on` does not require that match. It compares `(month, day)` tuples, so a person born on 29 Feb is still 54 on 28 Feb of a common year and attains 55 on **1 March**. Because 1 March is not `(2, 29)`, a valid 29-Feb member in a common year had no snapshot and was turned away with `CPFUnsupportedCase`.

The only verified-FRS case of this defect is **1972-02-29 attaining 55 on 2027-03-01** (2027 FRS is in this module; 2026 FRS would require a 1971-02-29 DOB, which is not a real calendar date).

A 29-Feb DOB is only valid in a leap year, and 55 ≡ 3 (mod 4), so the 55th anniversary year is **never** a leap year. There is no 29-Feb-on-29-Feb age-55 snapshot to accept. Leap-year behaviour of the shared rule is still tested, at ages whose anniversaries do fall on 29 Feb (52, 56, 60).

Other refusals (unverified FRS cohort, unconfirmed membership, property pledge, existing RA, invalid amounts or dates) are genuine unsupported cases and were left in place.

## 2. Fix

Added `_attained_age_date(born, age)` in `cpf_retirement_v26.py` (a verbatim copy of STAT-LEAPDOB's helper in `statutory_2026.py`, apart from the exception type: this copy raises `CPFUnsupportedCase` where that copy raises `core.ValidationError`; this branch does not depend on the unmerged `fix/statutory-leap-dob` work) and replaced the exact `(month, day)` check with:

```python
if today != _attained_age_date(birthday, 55):
    raise CPFUnsupportedCase('Only an exact 55th-birthday snapshot is supported; ...')
```

The helper returns `date(year, month, day)` when that calendar day exists, and **1 March** when 29 Feb does not exist in the target year. That is the first date `core.age_on` treats as the new age.

Money math is unchanged (still `Decimal`, same transfer order: SA first, then OA, up to cohort FRS). Ordinary DOBs still snapshot on their calendar birthday. Adjacent days, a non-existent 2027-02-29 `as_of`, unverified FRS cohorts, unconfirmed membership, property pledges, existing RA, and invalid amounts or dates still raise `CPFUnsupportedCase`. That is not true of every refusal: at `5452a46`, a birth year whose 55th anniversary falls after year 9999 (for example 9945 and later) raised a bare `ValueError` (`year 10000 is out of range`) from the helper instead of `CPFUnsupportedCase`. That edge is corrected in this follow-up (see §8).

**INTERNAL ASSUMPTION, not checked against the CPF Board or any statutory convention (Phase 7 external review skipped):** treating 1 March as the attained-age date in a common year is aligned with the engine's existing `core.age_on` behaviour only. It is documented in the `_attained_age_date` docstring.

## 3. Red / green

Tests were written first in `tests/test_cpf55_leap_dob.py` (synthetic 29-Feb DOBs only; valid leap-year birth dates).

- **Red** (parent `823ef72` source + new tests): `red-phase.log`, **4 failed, 14 passed**. The two 2027 1-Mar transition tests and the 1968-02-29 / 2023-03-01 cohort test failed with `CPFUnsupportedCase: Only an exact 55th-birthday snapshot is supported`. The helper import failed because `_attained_age_date` did not yet exist. Convention checks, ordinary-DOB regressions, adjacent-day refusals, and other unsupported-case tests already passed.
- **Green:** `green-phase.log`, **18 passed**, 0 failed.

The new tests cover: 1972-02-29 / 2027-03-01 monetary snapshots (FRS-filling, SA-excess, and below-FRS); adjacent-day and invalid 2027-02-29 refusals; 1968-02-29 / 2023-03-01 accepted by the date check and then refused as an unverified FRS cohort; leap-year 29 Feb dates at ages 52/56/60 not treated as the 55th snapshot; ordinary 28-Feb, 1-Mar, 1-Jun 2026 and 1-Jan 2027 regressions; and agreement of the helper with `core.age_on` in common and leap years.

## 4. Full suites

All runs used `/workspace/sweelah-baseline-venv` (Python 3.13.5) with `PYTHONPATH=.` in this worktree. Host previews on ports 8769–8773 were left running. No other worktree was checked out or edited. No preview was required on 8777.

| Suite | Result | Log |
|---|---|---|
| New tests, red | 4 failed, 14 passed | `red-phase.log` |
| New tests, green | **18 passed** | `green-phase.log` |
| `pytest -q -rs --ignore=tests/test_s016_browser.py` | **793 passed**, 0 failed, 1 dependency deprecation warning | `pytest.log` |
| Browser `tests/test_s016_browser.py -q -s` with `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` (real Chromium 156.0.8078.47) | **46 passed**; `axe WCAG checks PASS` | `browser.log` |
| Combined pytest + browser | **839 passed** (821 on main + 18 new) | — |
| Rule contracts `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` | **PASS 20/20**, run under `unshare -rn` with loopback up (its own :8769 inside the namespace; host previews 8769–8773 untouched) | `api.log` |
| Release documents `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Design assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

## 5. Visible UI output change: **No**

`service.evaluate()` for all three bundled households (`data/*household*.json`) is **byte-identical** to `origin/main`. None of those profiles has a 29-Feb DOB (`ui-compare.log`). Default UI chart text and "Baseline projected accessible assets" do not change. Labels and copy are unchanged.

`transition_at_55` is not called from `service.evaluate`, the HTTP API, or the shipped UI. It is a bounded reference used by unit tests. A user-edited 29-Feb profile still hits the separate `statutory_2026` crash (SWEELAH-STAT-LEAPDOB, unmerged on this branch) before any RA snapshot would run. G5X is not applicable: no labels, copy, or layout change, and no change to shipped sample output.

## 6. Residual risks

1. **Leap-day convention is an internal assumption.** 1 March in a common year follows `core.age_on` only. It has not been checked against the CPF Board or any statutory convention. Phase 7 (external review) is skipped.
2. **`statutory_2026` still crashes for 29-Feb DOBs** on this branch (`date(year, 2, 29)` in a common year). That is SWEELAH-STAT-LEAPDOB on `fix/statutory-leap-dob`, left untouched here by design.
3. **`projection_v22._anniversary` / issue #9** is a separate branch (`fix/issue-9-partial-month`) and was not merged into this worktree.
4. **A 29-Feb 55th anniversary cannot fall in a leap year** (55 ≡ 3 mod 4). Leap-year helper behaviour is unit-tested at ages 52, 56 and 60, not through a monetary `transition_at_55` call. Verified FRS years remain 2026 and 2027 only; 1968-02-29 / 2023-03-01 is now refused for the cohort limit, not the birthday check.

## 7. Constraints observed

No push, PR, merge, force-push or amend. Synthetic dates only; no NRIC, CPF account, bank or real user data; no secrets; no paid services or deploys; no Supermemory or connectors. Existing named worktrees (including `sweelah-issue-8`, `sweelah-issue-9`, `sweelah-stat-leapdob`, `sweelah-cxui-*`, `sweelah-qa-*`, `/workspace/sweelah`, `eng-onb-*`) were left untouched. Previews on 8769–8773 were not stopped.

## 8. Follow-up: SWEELAH-LEAPDOB-YEARCAP (QA G5 condition, 10 Nov 2026)

QA G5 at `5452a46` (PASS with conditions) found that `_attained_age_date` still raised a bare `ValueError: year 10000 is out of range` when `born.year + age` exceeds 9999. The 29-Feb fallback `except ValueError` also constructs a date in that year, so the overflow leaked out. This is unreachable for the verified 2026/27 FRS cohorts, but it contradicted the earlier claim that every other refusal raised `CPFUnsupportedCase`.

**Fix.** The helper now checks the target year against `date.min.year` / `date.max.year` (1–9999) before constructing a date, and raises `CPFUnsupportedCase` with a clear message: `Attained-age calendar year is outside the supported date range (1-9999)`. The 29-Feb → 1-Mar fallback is unchanged for in-range years.

**Tests** (written first) in `tests/test_cpf55_leap_dob.py`:
- `9950-01-15` at age 55 (year 10005) and the leap-day DOB `9944-02-29` at age 56 (year 10000) raise `CPFUnsupportedCase`, not a bare `ValueError`, both on the helper and via `transition_at_55` (the public-function leap-day case is `9948-02-29`, whose age-55 year is already past 9999).
- `9944-02-29` at age 55, the last in-range 29-Feb / age-55 anniversary, still returns `9999-03-01`.

Red: `yearcap-red.log`, **2 failed, 19 passed**. Both failures are `ValueError: year 10005 is out of range` from the helper. Green: `yearcap-green.log`, **21 passed**.

**Helper copy.** `_attained_age_date` is a verbatim copy of STAT-LEAPDOB's helper in `retirepilot/statutory_2026.py`, apart from the exception type (`CPFUnsupportedCase` here, `core.ValidationError` there).

**Manifests.** `docs_release/RELEASE_MANIFEST_v2.7.json` and `docs_v26/VERIFICATION_MANIFEST_v26.json` still pin the old `cpf_retirement_v26.py` hash. That is being handled by SWEELAH-MANIFEST-PINS on a separate branch; this commit does not touch manifests.

**Land order.** STAT-LEAPDOB, then #9 (`fix/issue-9-partial-month`), then CPF55, with no release in between. Consolidation of the three leap-day helpers follows after those merges.

### Suites re-run on this commit

All runs used `/workspace/sweelah-baseline-venv` (Python 3.13.5) with `PYTHONPATH=.` in this worktree. Host previews on ports 8769–8773 were left running.

| Suite | Result | Log |
|---|---|---|
| Year-cap tests, red | 2 failed, 19 passed | `yearcap-red.log` |
| Year-cap tests, green | **21 passed** | `yearcap-green.log` |
| `pytest -q -rs --ignore=tests/test_s016_browser.py` | **796 passed**, 0 failed, 1 dependency deprecation warning | `pytest.log` |
| Browser `tests/test_s016_browser.py -q -s` with `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` (real Chromium 156.0.8078.47) | **46 passed**; `axe WCAG checks PASS` | `browser.log` |
| Combined pytest + browser | **842 passed** (821 on main + 21 on this branch) | — |
| Rule contracts `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` | **PASS 20/20**, run under `unshare -rn` with loopback up (its own :8769 inside the namespace; host previews 8769–8773 untouched) | `api.log` |
| Release documents `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Design assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |
