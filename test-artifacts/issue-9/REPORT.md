# SWEELAH-ISSUE-9: partial-month overstatement (Refs #9)

- Task: SWEELAH-ISSUE-9 (CoS assignment, Sponsor-approved 10 Nov 2026 9:17pm SGT). Author: Engineering Lead.
- Worktree: `/workspace/sweelah-issue-9`. Branch: `fix/issue-9-partial-month`. Base: `origin/main` @ `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (fetched and confirmed 10 Nov 2026).
- Status: Implemented. Engineering suites green. Not yet verified by G5 (QA). Not pushed.
- Data: synthetic only. No NRIC, CPF account, bank or real-user data.

## 1. What the issue says vs. what main does now

Issue #9 reproduces this case: DOB 1974-05-20, horizon ends on the 53rd birthday (2027-05-20), income S$7,200 a month. The engine reported **S$36,000** for 2027, but the calendar-day value is **S$33,212.90**.

**That exact case already passes on main 823ef72.** The v2.7 import replaced the clipped-end denominator with `monthrange` in `projection_v22.py`. `tests/test_approved_decisions_v27.py::test_p0_terminal_month_proration_independent_reference` checks it. I re-ran it independently and got 33212.90.

Issue #9 also asks for these acceptance checks: anniversaries on the 1st, mid-month and last day; **leap years**; partial start and end months; and reconciliation of income, expenses, debt cash/CPF payments, interest and returns at the end of the horizon. I wrote an independent calendar-day oracle (`oracle_sweep.py`) and ran 225 profile/boundary combinations through it:

- main 823ef72: **43 mismatches, all for 29-Feb birthdays** (`oracle-sweep-main-823ef72.log`).
- this fix: **0 mismatches** (`oracle-sweep-fix.log`).

All non-leap anniversaries (1st, 20th, 31st, 31 Jan, 31 Dec, 28 Feb) and partial start months already matched the oracle on main.

## 2. Root cause

`projection_v22._anniversary()` sets every age boundary: the projection horizon, `starts_age`, `ends_age`, the retirement cutoff and `end_person_age`. For someone born on 29 Feb, it clamps the birthday to **28 Feb** in a common year. The engine's own age function, `core.age_on()`, says that person is still the younger age on 28 Feb and reaches the new age on **1 Mar**. Because the two disagree, the boundary falls one day early:

| Flow | Effect on main | Example (born 1976-02-29, S$7,200/mo, 2029) |
|---|---|---|
| `starts_age` income (e.g. a payout from age 53) | **Overstated**: starts on 28 Feb | 2029 income S$72,257.14 vs S$72,000.00 (+S$257.14) |
| `end_person_age` expense | Understated, so **net cash is overstated**: stops on 28 Feb | Feb spending 27/28 instead of 28/28 |
| Projection horizon / retirement cutoff / `ends_age` | Understated by one day | 2029 income S$14,142.86 vs S$14,400.00 |

The terminal-month *denominator* is correct on main. What was wrong is the *boundary date* that goes into the overlap calculation. Fixing `_anniversary` fixes every age-bounded flow at once.

## 3. Fix (minimal, one function)

`retirepilot/projection_v22.py::_anniversary` now returns the first date on which `age_on(dob, date) == age`. That is 1 Mar when the birth day does not exist in the target month, which only happens for 29 Feb. All other dates are unchanged. The arithmetic stays in Decimal, and no other engine code changed.

## 4. Red/green evidence

New file: `tests/test_issue9_partial_month.py` (40 tests). Expected values come from an independent calendar-day oracle in the test, not from the engine.

- **Red** (on 823ef72 source + new tests): `red-phase.log`, **10 failed, 30 passed**. The 10 failures are all 29-Feb cases, e.g. `test_leap_day_birthday_starts_age_income_not_paid_a_day_early`: `{2029: '72257.14'} != {2029: '72000.00'}`.
- **Green** (after the fix): `green-phase.log`, **40 passed**.
- The 30 tests that pass on both are new golden coverage for the other acceptance checks:
  - terminal-month income and expense for anniversaries on the 1st, mid-month and last day, 31 Jan, 31 Dec and 28 Feb, each with 3 as-of dates;
  - the issue's reference case (33,212.90);
  - a Feb-29 birthday falling in a leap year;
  - a terminal month with debt cash and CPF payments, debt interest, portfolio gain and cash interest, all prorated 19/31 against the full calendar month.

## 5. Full suites (this worktree, Python 3.13.5 via `/workspace/sweelah-baseline-venv`)

| Check | Result | Log |
|---|---|---|
| Release documents `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Design assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |
| `pytest -q -rs` (full) | **861 passed**, 0 failed, 0 skipped (821 existing + 40 new) | `pytest.log` |
| Rule contracts `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| Browser `tests/test_s016_browser.py -v -s` (real Chromium) | **46 passed** (71 PASS lines) | `browser.log` |
| API `audit/run_api_checks.py` | **PASS 20/20**, run under `unshare -rn` (its own :8769 inside the namespace; host previews 8769-8773 untouched) | `api.log` |

Exit codes: `exits.txt`. Environment: `env.txt`.

## 6. Visible UI change: **No** for every shipped sample. Yes only for user-edited 29-Feb profiles.

- No HTML, CSS, copy, layout or API schema changed.
- `service.evaluate()` projection output for all three bundled households (`data/*household*.json`) is **byte-identical** before and after the fix. None of them has a 29-Feb DOB. So the default UI chart and "Baseline projected accessible assets" text do not change.
- The UI takes editable JSON. For a profile with a **29 Feb DOB** (none ships), the projection numbers shown (chart points, "Baseline projected accessible assets", combined-shock difference) can shift by about one day of the affected flows. For example, a S$7,200/mo flow moves by S$257.14 in that year. No labels or text change.
- Recommendation: G5X is not required by the "visible UI output changes" rule for shipped content. CoS to decide whether the 29-Feb numeric case counts.

## 7. Residual risks / follow-ups (not changed here, out of scope)

1. **Leap-day convention is an assumption.** I aligned the boundaries to the engine's existing `age_on`, where a 29-Feb person reaches the new age on 1 Mar in common years. I did not verify the CPF Board/statutory convention. That needs finance review (independent reviewer not engaged).
2. **`statutory_2026` crashes for 29-Feb DOBs.** Line ~45 does `date(born.year+threshold, born.month, born.day)`, so `employee_ow_cpf(dob='1972-02-29', month='2027-03', ...)` raises `ValueError: day is out of range for month`. Separate CPF-rate module; suggest a separate ticket.
3. Partial-month returns are prorated linearly, as `monthly_rate * fraction`, not as `(1+r)^fraction - 1`. Linear is slightly higher for fractions below 1 (about 1e-6 relative per partial month). This is intended and documented by the new test, not changed.
4. Issue #9 says not to close until a reviewed result is linked to GitHub CI. This commit uses "Refs #9" only.
