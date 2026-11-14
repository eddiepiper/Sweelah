# SWEELAH-ATTAIN-CORE: one attained-age helper in core; projection anniversary year cap

**Status: Implemented but unverified (pending QA G5).**

- Branch `refactor/attained-age-core`, worktree `/workspace/sweelah-attain-core`, from main `5fe3ec8b6448d94d4a15dc18f1f38c2a58508e76` (after #23 STAT-LEAPDOB b5e81b4, #24 #9 06c96aa, #25 CPF55 3163ffb, #26 #8 5fe3ec8). Not pushed.
- Synthetic data only. No secrets. No manifest was rewritten. The pinned-file hashes in §8 are for the later manifest-pin ledger refresh.
- **INTERNAL ASSUMPTION (unchanged by this refactor):** a person born on 29 Feb attains each new age on **1 Mar** in a common year, matching `core.age_on`. This was not checked against the CPF Board or any statutory convention; Phase 7 external review was skipped. The label appears in `core.attained_age_date`, both wrappers, `projection_v22._anniversary` and `tests/test_attain_core.py`.
- **QA G5 (90112d4): PASS with conditions.** The report-only conditions are addressed in the follow-up commit; see §11.

## 1. What moved

| Before (main 5fe3ec8) | After |
|---|---|
| `statutory_2026._attained_age_date(born, age)`: its own copy, year cap raises `core.ValidationError` | Thin wrapper: `_core.attained_age_date(born, age, error=ValidationError)` |
| `cpf_retirement_v26._attained_age_date(born, age)`: a byte-for-byte copy apart from the exception, raises `CPFUnsupportedCase` | Thin wrapper: `_core.attained_age_date(born, age, error=CPFUnsupportedCase)` |
| `projection_v22._anniversary(dob_str, age)`: its own `monthrange` variant, **no year cap** | `_core.attained_age_date(date.fromisoformat(dob), age, error=ValidationError)` |
| none | **New** `core.attained_age_date(born, age, *, error=ValidationError)`, the single implementation |

The wrapper names and signatures are kept. Existing tests import `_attained_age_date` from both modules, and `_band_index`, `transition_at_55` and the projection callers are unchanged.

Call sites (`rg -n "_attained_age_date|_anniversary|attained_age_date" retirepilot/*.py`):
- `statutory_2026._band_index`, line 55 → `_attained_age_date` → core
- `cpf_retirement_v26.transition_at_55`, line 54 → `_attained_age_date` → core
- `projection_v22`, lines 51, 52 and 56 (`_active_fraction_stream`: starts_age, ends_age, retirement_age), line 62 (`_active_fraction_expense`: end_person_age), line 82 (`project_monthly`: projection_end_age horizon) → `_anniversary` → core

The full source diff is in `source.diff` (4 files, +41/−34).

## 2. Exception mapping per module

| Module | Out-of-range year (`born.year+age` outside 1–9999) | Type hierarchy | HTTP mapping |
|---|---|---|---|
| statutory_2026 | `core.ValidationError` (unchanged) | ValueError subclass | 422 via api.py `except (ValueError,…)` |
| cpf_retirement_v26 | `CPFUnsupportedCase` (unchanged; e.g. 9945+ DOB at 55, 9944-02-29 at 56) | ValueError subclass | 422 via the same catch |
| projection_v22 | **`core.ValidationError` (new)**. Before: raw `ValueError("year N is out of range")` for years 0 to −2³¹ and 10000 to 2³¹−1; `OverflowError` only beyond the C-int range (year > 2³¹−1 or < −2³¹) | ValueError subclass | 422. Before: **422 for the raw ValueError**; **500 only for the OverflowError cases**, because api.py catches only ValueError/KeyError/TypeError. See §3(c) |

The message is the same in all three: `Attained-age calendar year is outside the supported date range (1-9999)`.

**Why ValidationError for projection:** `project_monthly` already reports every invalid input with `core.ValidationError`: missing groups, incomplete records, an out-of-bound projection_end_age, an invalid horizon, rates ≤ −100% and unknown scenario targets. `ValidationError` is what `/api/evaluate` maps to 422. `CPFUnsupportedCase` belongs to the CPF reference module and is not imported by projection. The cap is checked before any `date` or `monthrange` call, so even a 10**20 age cannot reach `OverflowError`.

## 3. Behaviour differences between the old copies (flagged, not silently chosen)

1. **statutory vs CPF:** the logic, year cap and message are identical. The only difference is the exception class. This is kept through the `error=` parameter.
2. **projection vs the other two:**
   - (a) It takes an ISO string, not a `date`. The wrapper parses it first, as before.
   - (b) Its 29-Feb fallback was `if d.day > monthrange(year, d.month)[1]: date(year, d.month+1, 1)`, not `try/except ValueError → date(year, 3, 1)`. For any valid DOB, only 29 Feb can exceed the month length, so both give 1 Mar. (`month+1` would break for December, but that case cannot occur.) The sweep in §4 confirms they are equal wherever the old code returned a date.
   - (c) **It had no year cap.** The precise 500 → 422 change, probed on main 5fe3ec8 (`out-of-range-probe.log`, script `out-of-range-probe.py`; synthetic RP-SYNTH profile, DOB 1974-05-20, `/api/evaluate` through TestClient):
     - **Already 422 on main**, with a raw message such as `year 10974 is out of range`:
       - starts_age 8026 (year 10000), 9000, 9999 and 1000000;
       - starts_age −1974 (year 0), −1975 and −1000000;
       - end_person_age 9000 and 1000000;
       - a projection horizon in year 10045 (DOB 9950-01-15).
       - Years ≥ 10000 and year 0 were therefore **not** 500 on main. Only the message changes, to the shared "outside the supported date range (1-9999)".
     - **500 on main (Internal Server Error)**: only overflow-scale values, where `datetime.date(...)` (projection_v22.py line 41 on main) raised `OverflowError`:
       - starts_age 2147483647 (2³¹−1), 2⁶², 2⁶³−1, 2⁶³ and 10²⁰;
       - end_person_age 2⁶³ and 10²⁰.
       - Bisected threshold on main: year 2147483647 gives ValueError, and year 2147483648 (> 2³¹−1) gives `OverflowError: signed integer is greater than maximum`. On the negative side, year −2147483648 gives ValueError and year −2147483649 gives OverflowError.
     - **On 90112d4**, every case above returns 422 with the shared message. The 200 cases are unchanged: starts_age 8025 (year 9999), and end_person_age 7990 and 7991.
     - Correction to the 90112d4 text: the OverflowError came from `datetime.date(...)`, not from `calendar.monthrange`.
   - This is the one intended behaviour change: out-of-range years now raise `ValidationError` with the shared message, and only the overflow-scale inputs move from 500 to 422. Validation does not bound `starts_age`/`ends_age`/`end_person_age`, so this path is reachable with synthetic input. `projection_end_age` is bounded at 110, but a DOB of 9950 still overflows the horizon (that case was already 422 on main).
   - In-range results are unchanged.

## 4. Behaviour-equivalence evidence

`tests/test_attain_core.py` freezes verbatim copies of the three old implementations as oracles (`_OLD_statutory`, `_OLD_cpf`, `_OLD_projection`).

The sweep covers 103 synthetic DOBs:
- 15 years: 1, 4, 1900, 1944, 1952, 1960, 1964, 1971, 1999, 2000, 2024, 9944, 9945, 9950 and 9999;
- each on 01-01, 02-28, 03-01, 05-20, 05-31 and 12-31;
- plus 13 29-Feb DOBs from year 4 to 9996.

Each DOB is checked at 21 ages: −2001, −2000, −1, 0, 1, 3, 4, 45, 55, 56, 59, 60, 65, 70, 95, 96, 100, 110, 9998, 9999 and 10000. That is 2,163 (DOB, age) pairs per comparison.

- `core.attained_age_date` vs `_OLD_statutory` and (with `error=CPFUnsupportedCase`) vs `_OLD_cpf`: the outcome tuple is equal, meaning the same date, or the same exception type and message.
- `statutory_2026._attained_age_date` / `cpf_retirement_v26._attained_age_date` vs the oracles: equal. These **passed before the change too**, which shows the oracles faithfully copy the old code.
- `projection_v22._anniversary` vs `_OLD_projection`: equal wherever the old code returned a date, and `age_on(dob, result) == age` holds.
- A spy test confirms that all three modules route through `core.attained_age_date` with ValidationError / CPFUnsupportedCase / ValidationError.
- End to end: `service.evaluate()` was run on the 3 bundled households as shipped, and on 3 synthetic 29-Feb primary-DOB variants of each (1964, 1972 and 1960), for 12 runs. The sha256 of the sorted JSON output is **identical** between main 5fe3ec8 and this branch (`ui-compare.log`). There is no visible UI or output change.

## 5. TDD red → green

| Phase | Result | Log |
|---|---|---|
| Red (new tests vs main code) | **113 failed, 207 passed** | `red-phase.log` |
| Green | **320 passed** | `green-phase.log` |

The red failures were:
- 103 × core-helper sweep and 3 helper tests (no `core.attained_age_date`);
- 1 spy test;
- 4 × projection `_anniversary` out-of-range: `ValueError: year 10005/10000/0 is out of range` and `OverflowError: Python int too large to convert to C long`;
- `project()` horizon past 9999 (`ValueError: year 10045 is out of range`);
- `project()` with `starts_age=10**20` (`OverflowError`);
- `/api/evaluate` with `starts_age=10**20`: **500** instead of 422.

The 207 that passed in red are the wrapper/oracle equivalence tests, the in-range projection equivalence tests and the 9944-02-29 → 9999-03-01 test.

Process note: in the first red capture, the `_outcome` test helper did not forward `error=`. I fixed the test, reverted the implementation, recaptured the red log above against main code, then re-applied the implementation. The logs on disk are the final ones.

## 6. Full suites

All runs used `/workspace/sweelah-baseline-venv` with `PYTHONPATH=.` in this worktree. Host previews on ports 8769–8773 were left running, and no other worktree was touched.

| Suite | Before (main 5fe3ec8) | After | Log |
|---|---|---|---|
| `pytest -q -rs --ignore=tests/test_s016_browser.py` | 944 passed | **1264 passed** (944 + 320 new), 0 failed, 1 dependency deprecation warning | `pytest-before.log`, `pytest.log` |
| Browser `tests/test_s016_browser.py -q -s` (AXE_CORE_PATH=/tmp/cxui-axe/…/axe.min.js) | n/a | **46 passed**, `axe WCAG checks PASS` | `browser.log` |
| Rule contracts `audit/run_rule_contracts_v22.py` | n/a | **498 passed, 0 failed** | `rules.log` |
| API `audit/run_api_checks.py` under `unshare -rn` + `ip link set lo up` | n/a | **PASS 20/20** | `api.log` |
| `scripts/verify_release_documents.py` | n/a | 9 artifacts, errors=0 | `release.log` |
| `design/sweelah/verify_assets.py` | n/a | PASS 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

## 7. Mutation spot-checks (both reverted; `cmp` confirms core.py restored)

| Mutant | Result | Log |
|---|---|---|
| M1: year cap removed from `core.attained_age_date` (`if False:`) | **218 failed**, 153 passed across test_attain_core + test_statutory_leap_dob + test_cpf55_leap_dob | `mutation-cap.log` |
| M2: 29-Feb fallback changed to 28 Feb | **41 failed**, 279 passed in test_attain_core | `mutation-leap.log` |

Under M1, the failing tests included:
- all 4 projection out-of-range tests;
- both `project()` overflow tests and the API 422 test;
- the existing STAT and CPF55 "refuses calendar year past 9999" tests.

## 8. sha256 of changed tracked .py files

core.py, statutory_2026.py, projection_v22.py and cpf_retirement_v26.py are **pinned files**. These values are for the later manifest-pin ledger refresh. No manifest was edited here.

| File | Before (5fe3ec8) | After (this commit) |
|---|---|---|
| retirepilot/core.py | 46cbcd18e12f0282f641e6056aa3b0f10dd3c6a901deecb0201bfce2fb72dbf9 | 6b00cdfa9a2370c6b9fe9ca93c4fd80a8b7e74abd16efec8c9389b17910fa5ce |
| retirepilot/statutory_2026.py | 5075d5b435acb07946771d4442819b2a3109976029fe2b35ec30440d04f9a4e6 | 765195814552eaedce04047f6e696ec35c3c471c4d41808541c7e37c93433617 |
| retirepilot/cpf_retirement_v26.py | e8d989190671f4f2dada364dc94a4b131ab6580e0157dd010e14a52d1e42eb41 | ee2aa8560ca10bb9f885f52d3fc544fdde6f10cc4bfb71f8e53a56ba26620a25 |
| retirepilot/projection_v22.py | 092b4a400a18848fd3916d27ef6391fb465f590b3294890fdda247c44baf1c2f | 7e5004aeb9494be9eb0b151ea6f62b47740498bded300171f378dff9e1feed7a |
| tests/test_attain_core.py (new) | — | 622bbe0bc8de270102f1338ffc3ff1dde4af92d2c81b93bc354beb65e42fc993 |

Raw values are also in `sha256-before.txt` and `sha256-after.txt`.

## 9. Land-order notes

Every git fact in this section was re-verified for the G5 follow-up; the commands and output are in `sec9-git.log`.

- This branch edits the four pinned files. MANIFEST-PINS lands last, so its single ledger refresh should use the hashes on main at the final SHA. The after-values in §8 hold only if nothing else touches these files.
- **CPFLIFE dbc2d84's merge base is `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (823ef72), not 5fe3ec8.**
  - `git merge-base 90112d4 dbc2d84` and `git merge-base 5fe3ec8 dbc2d84` both return 823ef72.
  - 823ef72 is an ancestor of 5fe3ec8, and `core.py` is unchanged between them.
  - Forcing `--merge-base 5fe3ec8` is therefore not a valid trial merge.
- **CPFLIFE edits `core.py` in three hunks** (`git diff -U0 823ef72 dbc2d84 -- retirepilot/core.py`):
  - `@@ -15,0 +16,3 @@`: CPF LIFE start-age constants;
  - `@@ -95,0 +99,9 @@`: the `validate()` CPF LIFE start-age refusal;
  - **`@@ -190,0 +203,3 @@`**: a third hunk, also in `validate()`.
  - ATTAIN-CORE's only `core.py` hunk is `@@ -40,0 +41,27 @@`, after `age_on`. None of the hunks overlap.
- **Trial merge:** `git merge-tree --write-tree 90112d4 dbc2d84` (automatic merge base 823ef72) gives tree `78c37ecd1127054a4de9c21be314514eebd8bc67`, exit 0, clean. This matches QA and CoS.
- Other open branches: #2 25e4e56, #5 de9d27b, #4 2d03c9c, #3 c32ede1 and MANIFEST-PINS 22bb38f touch none of the four files.
- **The manifest-pin ledger test already fails on main** (`manifest-pins-ledger-probe.log`). I took `tests/manifest_pin_ledger.json` and `tests/test_manifest_pins.py` from 22bb38f and ran them in temporary `git archive` trees, so no worktree was touched.
  - **On 5fe3ec8: 1 failed, 10 passed.**
    - DRIFT on `projection_v22.py`: the ledger records c6889d3a…, which is `git show 823ef72:retirepilot/projection_v22.py | sha256sum`; main has 092b4a40…. The change comes from #9 (11425e0, 3f9884f).
    - UNRECORDED MISMATCH on `statutory_2026.py` and `cpf_retirement_v26.py`. These come from the merged leap fixes: 22ef888 and 339ecea for statutory, 5452a46 and 08317d8 for CPF, per `git log 823ef72..5fe3ec8`.
  - **On 90112d4: 1 failed, 10 passed.** It additionally reports DRIFT on `core.py` (the ledger records 46cbcd18…; actual 6b00cdfa…) and an UNRECORDED RELEASE mismatch on `core.py`.
  - This is expected. The ledger is PROVISIONAL, and CoS's plan is a single ledger refresh on the final main SHA.
  - That refresh must cover all four pinned files, including adding the cpf and statutory entries. It must also decide how CPFLIFE's `test-artifacts/cpf-life-start-age/samples-sha256-*.json` files are treated, because the ledger test reads them as manifests (QA condition 5).
- Once CPFLIFE lands, `core.py`'s final hash will differ from the §8 after-value. QA measured the merged-tree `core.py` at 16e5a5bb….

## 10. Files in the commit

- `retirepilot/core.py`, `retirepilot/statutory_2026.py`, `retirepilot/cpf_retirement_v26.py`, `retirepilot/projection_v22.py`
- `tests/test_attain_core.py`
- `test-artifacts/attain-core/`:
  - `REPORT.md`, `source.diff`, `sha256-before.txt`, `sha256-after.txt`
  - `*.log` (force-added): `red-phase`, `green-phase`, `pytest-before`, `pytest`, `browser`, `rules`, `api`, `release`, `assets`, `ui-compare`, `mutation-cap`, `mutation-leap`
  - Added in the G5 follow-up: `out-of-range-probe.log`, `out-of-range-probe.py`, `sec9-git.log` and `manifest-pins-ledger-probe.log` (force-added)
- No PNGs. The untracked `test-artifacts/cxui-*` / `qa-*` directories written by the browser suite are not staged.

## 11. QA G5 follow-up (report-only)

The verdict is at `/workspace/qa-sweelah-attain-core/qa/attain-core-90112d4/VERDICT.md`: PASS with conditions. This follow-up commit changes only this REPORT and adds the evidence logs. There are no code or test changes, so the §8 hashes are unchanged.

| QA condition | Where addressed |
|---|---|
| 1. INTERNAL ASSUMPTION label for 29 Feb → 1 Mar | Preamble |
| 2. Preamble pointed to §7 for hashes | Now points to §8 |
| 3. §9: third CPFLIFE core.py hunk (@203), merge base 823ef72, ledger test already failing on main | §9, verified with git (`sec9-git.log`, `manifest-pins-ledger-probe.log`) |
| 4. Precise 500 → 422 statement | §2 table and §3(c), probed on main and on 90112d4 (`out-of-range-probe.log`) |
| 5. Ledger refresh scope | §9 last bullets. This is for the MANIFEST-PINS refresh on final main, not this branch |

**Discrepancy flagged:** the follow-up brief described the old 500s as "overflow, years ≥ 10000 or 0". The probes show years ≥ 10000 and year 0 already returned **422** on main, with a raw ValueError message. Only overflow-scale years (> 2³¹−1 or < −2³¹) returned 500. That matches QA's finding that 9000–1e6 was already 422. The report states the probed behaviour.

Status: **Implemented but unverified (pending QA re-check of the report conditions).**
