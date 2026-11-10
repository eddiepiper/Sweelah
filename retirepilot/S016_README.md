# S016 parent-care cost preview

Local and synthetic only. This is a bounded preview, **not** a fully implemented
life-event engine, user-validated tool, entitlement calculation or financial advice.
No accounts, products, sharing, external services or persistent records.

## Run

From the repository root with existing requirements installed:

```sh
python -m uvicorn retirepilot.api:app --host 127.0.0.1 --port 8766
```

Open http://127.0.0.1:8766/sweelah for Life Line → Care for family.
The original research dashboard remains at `/` and is unchanged.

The new runtime screen reuses the care scenario-panel, field-label, summary-sheet,
secure-notice and button patterns from the approved
`design/sweelah/prototypes/SweeLah_Onboarding_and_Dashboard_With_Floating_Clouds.html`.
It is a separate served file, not a modified or newly hashed design artifact.
All preserved prototypes, ASSET_MANIFEST.json and its verifier are unchanged.
The new screen uses 16px body text, the preserved ink and #1C806E green tokens, visible keyboard focus
and reduced-motion support rather than the prototype's small/light text.

## API

`POST /api/scenarios/S016/preview` accepts:

```json
{"synthetic_profile_id":"RP-SYNTH-S016","params":{"additional_care_cost_monthly":"1200","months":12}}
```

The only calculation inputs are a positive cost up to S$100,000 inclusive, with
at most two decimal places, and integer months 1–120. Neither
field defaults or prefills. Fractional months are always refused; positive decimal
costs are accepted up to two places. The UI and endpoint strip leading `S$` and
commas (for example `1,200.5`).
Sub-cent precision is refused before the preview call, with HTTP 422 and no result:
“Enter an amount with up to 2 decimal places, for example 1200.50.”
Precision is checked without float rounding: JSON fractional tokens are parsed as
Decimal for this endpoint, and the UI counts fractional digits using the input
string and an integer exponent. Other endpoints retain their default JSON parser.
Exponent forms within the amount cap are accepted when their expanded Decimal scale has at most two
fractional places: `1e2` = 100, `1e-2` = 0.01, `1.005e2` = 100.50; `1e-3` is refused.
Explicit trailing fractional zeros count: `1.50` is accepted, `1.500` is refused.
`1.005` (string or JSON number) is refused, while `1.50` × 12 displays S$18.00.
The existing preview arithmetic is unchanged.
The synthetic fixture identifier is a local-development guard, not authentication
or permission to process real financial records. Do not expose this server publicly.

The endpoint validates bounds and precision before delegating to the unchanged
`preview_priority_scenario` arithmetic.
It returns `extra_monthly_cost: "1200.00"`, `months: 12`,
`period_cash_cost: "14400.00"`, the unchanged meaning/status, explicit limitations,
`synthetic_only: true` and `may_post_to_household_projection: false`.
No household evaluation or dashboard state is changed. The registry's
`implemented_component` remains false.

Flat monthly cost only: no inflation, assumed subsidy, grant, insurance payout,
MediSave, caregiver wage loss, care leave or entitlement. These are limitations,
not input fields or inferred benefits. Explicit limitation copy takes precedence
over the request to omit benefit-related copy entirely. There is no product
library/suggestion, persona score, sibling sharing or affordability claim.

Missing/invalid calculation values return HTTP 422 with the existing `detail`
convention; missing/non-synthetic fixture IDs return 403, malformed JSON 400.
The shared `_amount` zero-cost error still says “nonnegative amount required”.
This endpoint checks positivity first and returns “must be more than 0”; the UI
maps stable field/code pairs to plain-language field messages. Recommended follow-up: correct the shared positive-only wording
in a separately approved compatibility change, not in this feature.

## Tests

```sh
python -m pytest -q
PYTHONPATH=. python audit/run_rule_contracts_v22.py
python audit/run_api_checks.py
python scripts/verify_release_documents.py
python design/sweelah/verify_assets.py
python -m pytest -q -s tests/test_s016_browser.py
```

The browser cases are automatically collected by the existing pytest CI command.
They start the actual localhost server and drive the actual UI, not a mock server.
They require already-installed Node Playwright and Chromium; no dependency/browser
is downloaded. They skip with a clear reason if these optional tools are absent.
To select installed tools explicitly:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/node_modules/playwright \
S016_CHROMIUM=/absolute/path/to/chrome \
python -m pytest -q -s tests/test_s016_browser.py
```

The runner also discovers local Node Playwright in the npm cache and Chromium in
the Playwright browser cache. UI assertions cover desktop/mobile, field errors,
focus, ARIA, retained values, amount normalization, real API refusal/network
failure, status/limitations and unchanged projection/dashboard values.
The accessibility case also checks keyboard-only submission, target dimensions
and selected text/background contrast pairs. It runs axe if an offline `axe-core`
package or `AXE_CORE_PATH` is supplied; otherwise it explicitly reports the gap.
Screenshots go to `test-artifacts/s016/` (local artifacts, do not commit).
An independent WCAG audit, screen-reader review and real-user validation are not
claimed. Python 3.13 local execution does not replace CI's Python 3.11 verification.


## CXUI-001-FIX: customer-facing corrections

Status: **Verified** locally by the automated checks below; independent QA/designer
re-verification and merge approval are still pending.
Based on CXUI-001's audit of `78f71c4`; only the served S016 screen, its endpoint,
S016 tests/smoke assertions and this document change. No dashboard, preserved
prototype, shared scenario arithmetic or dependency change.

- One full limitations notice stays visible in setup, validation/refusal and result
  states. It names subsidies/grants, CareShield LIFE/insurance, MediSave, lost pay /
  unpaid leave and financial-advice limitations without repeating raw API copy.
- Internal status and meaning stay in the API contract, not the rendered UI.
  The practice/synthetic-data safeguard remains in plain language.
- Editing clears only that field's inline error, ARIA invalid state and summary
  link. Other errors and their focusable links remain until edited/resubmitted.
- Server/network/unrecognised 422 failures say “Something went wrong”, keep both
  values, and never label valid answers as wrong or display raw server detail.
- S016 field-validation responses retain their existing string `detail` and add
  `field` and `code`. Fields: `additional_care_cost_monthly`, `months`. Cost codes:
  `missing`, `numeric`, `precision`, `positive`, `too_large`; duration code: `months`.
  Unknown field/code pairs fall back to the neutral retry message. Envelope/JSON
  errors can remain detail-only; no prefix matching is used by the client/server.
- The amount cap is a prototype typo/plausibility guard, not an affordability or
  entitlement judgement: **S$100,000/month**, inclusive. Months remain **1–120**.
  Over-cap finite decimals and positive exponent overflow (e.g. `1e400`) say
  “Enter an amount no more than S$100,000.” Infinity/NaN-like amounts get the existing
  numeric message. Both client and endpoint refuse invalid values without a 500.
  Existing precision/positive/months messages are retained. Exponent notation is
  intentionally still accepted **within bounds and the two-place scale rule**,
  preserving the existing API/browser contracts rather than changing input syntax.
- Green, coral wordmark and uppercase eyebrows now match preserved design tokens.
  Existing ink, cream, mint, panel/summary/notice patterns and accessible text sizes
  remain. Main section/result headings are h2; the nested error-summary title is h3.
  The header's “Back to overview” link remains `/` and has a minimum 44px height.
  Block-level summary links keep mobile bullets beside each item's first line.

### Defect-to-regression mapping

All browser cases below are `test_s016_real_browser[case]` in
`tests/test_s016_browser.py`, implemented in `tests/browser/s016.cjs`.

| Defect (all Verified locally) | Change file(s) | Proving case/test |
|---|---|---|
| D01 | `retirepilot/s016.html` | `cxui-d01`: no raw status rendered |
| D02 | same | `cxui-d02`: full notice in setup/result/return |
| D03 | same | `cxui-d03`: each edit retains the other field's error/link/ARIA |
| D04 | same | `cxui-d04`: no raw meaning repetition |
| D05 | same | `cxui-d05`: plain copy, practice safeguard retained |
| D06 | same | `cxui-d06`: 500/403/network neutral retry, values retained |
| D07 | `retirepilot/s016.html`, `retirepilot/api.py` | `cxui-d07`; `test_cxui_d07_amount_cap`, `test_cxui_d07_nonfinite_cost`, `test_cxui_d07_months_cap`, `test_cxui_d07_upper_boundary`, `test_cxui_d07_raw_json_overflow_and_nonfinite` in `tests/test_s016_parent_care.py` |
| D08 | `retirepilot/s016.html` | `cxui-d08`, `cxui-mobile375`: wrapped-link geometry and no overflow |
| D09 | same | `cxui-d09`: computed token colours/uppercase; axe in setup/error/result |
| D10 | same | `cxui-d10`: visible heading sequence in setup/error/result; axe best-practice |
| D11 | same | `cxui-d11`: header link measured at least 44×44px |
| Structured errors | `retirepilot/api.py`, `retirepilot/s016.html` | `cxui-mapping`; `test_cxui_structured_field_errors`; S016 precision smoke assertion in `audit/run_api_checks.py` |

The old exact error-body assertions are strengthened to include the additive
field/code metadata while checking the unchanged precision detail verbatim.
No non-S016 API smoke assertions change.

### Local evidence and follow-ups

Use the existing venv `/workspace/sweelah-baseline-venv` and supply the installed
axe script via `AXE_CORE_PATH` for the complete offline browser audit. The new CXUI
cases save desktop (1280px) and mobile (375px) setup/result/field-error screenshots,
server-error screenshots, bullet geometry and axe WCAG/best-practice JSON to
`test-artifacts/cxui-001/`. Suite stdout/stderr logs and red-phase failures are
also retained there, uncommitted. No screenshots contain real financial records.

Proposed follow-up (D09, deliberately not built): integrate the full SweeLah
Home / Life Line / Ask Swee / My Moves navigation and Swee artwork when the
standalone screen is incorporated into an approved product shell. No fake links,
new artwork, external assets or changes to the dashboard were introduced.
Independent QA/designer re-verification remains required before merging. Manual
screen-reader, non-Chromium, real-device and real-user checks remain unverified.


### CXUI-001-FIX verification results

All commands run in `/workspace/sweelah-cxui-fix` with the existing Python 3.13
venv activated; `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` is
supplied for pytest/browser checks. Chromium: 156.0.8078.47; axe-core: 4.14.0.

| Command | Verified result |
|---|---|
| `python scripts/verify_release_documents.py` | 9 artifacts, 0 errors |
| `python design/sweelah/verify_assets.py` | 6 prototypes + 15 assets, 21/21 hashes match |
| `python -m pytest -q` | 793 passed, no failures/skips; 1 dependency deprecation warning |
| `PYTHONPATH=. python audit/run_rule_contracts_v22.py` | 498/498 passed, 0 failed |
| `python audit/run_api_checks.py` | PASS, 20 checks |
| `python -m pytest -q -s tests/test_s016_browser.py` | 21 passed, no failures/skips |

The 9 final CXUI axe JSON reports show 0 WCAG/best-practice violations.
`git diff --check` passes; diff confirms `/`'s `retirepilot/ui.html` and all of
`design/sweelah/` are byte-unchanged from `78f71c4`. The `nonmutation` browser case
also verifies the dashboard's rendered snapshot and household evaluation remain
unchanged after preview. The one warning is Starlette TestClient's deprecated
`anyio.abc.BlockingPortal` alias, not an application error. Python 3.11 CI remains
a separate verification after the CoS publishes; no push or merge was performed.


## CXUI-001-FOLLOWUP: residual Low items from the G5X re-audit of `3f396aa`

Status: **Verified** locally by the automated checks below; independent QA (G5) and
designer (G5X) re-verification are still pending. Branch `fix/cxui-001-followup`
from `397a0bd`. Only `retirepilot/s016.html`, S016 tests and this document change.
`retirepilot/api.py`, the dashboard at `/`, preserved prototypes and the design tree
are unchanged. This section supersedes two statements in CXUI-001-FIX above: the
header link label, and browser acceptance of exponent notation.

| Item | Change (`retirepilot/s016.html`) | Proving case/test |
|---|---|---|
| R-D01 | Header link relabelled “Back to RetirePilot lab” (still `/`, still 44px). No SweeLah home exists, so none was invented. | `cxuifu-rd01`, `cxuifu-rd01-375` (label, href, 44px, no “overview”, destination title, axe); `test_cxuifu_static_page_copy_and_style` |
| R-D02 | Any field edit removes the general “Something went wrong” message and hides the summary if no field links remain. Only the edited field's own error/link/ARIA clear (D03 kept). | `cxuifu-rd02`, `cxuifu-rd02-375` (network failure cleared by a cost edit and by a months edit; server-mapped and client months errors survive a cost edit; recovery; axe) |
| R-D03 | `.error-summary h3{margin-top:0}` | `cxuifu-rd03`, `cxuifu-rd03-375` (computed 0px, heading flush with padding in field and server error states; axe); static test |
| Wording | Dropped “no assumed entitlement”. The notice now ends “It uses a flat monthly amount with no inflation.” | `cxuifu-wording` (setup/result/return); static test; `success` assertion updated |
| Exponent | The browser now accepts plain decimals only. `1e2`, `1E2`, `1e-3`, `1.005e2`, `1e400` and `2e+3` get “Enter numbers only, for example 1200.” and are not sent to the API. | `cxuifu-exponent`; `cxui-d07` and `precision`/`mobile375` assertions updated (see below) |

Interpretation decisions:
- R-D01: relabel rather than repoint, because no customer SweeLah home is served. The
  label names the page it opens (title “RetirePilot | Financial Planning Lab”).
- Exponents are refused in the customer UI only. The API contract that documents
  exponent acceptance within bounds and the two-place rule is unchanged, and no API
  test or smoke assertion changed. Direct API callers still get `1e2` = 100.
- Updated browser assertions: in `cxui-d07`, `1e12` and `1e400` now expect the numeric
  message (plain `100000.01`, `999999999999` and `100001` still expect the cap message).
  In `precision`/`mobile375`, `1e-3` was dropped from the precision list (now numeric,
  covered by `cxuifu-exponent`), and the `1e2` success row became `100`.

Follow-ups (not built): full SweeLah navigation and Swee artwork (D09). D05 residual
copy (“Practice mode: use made-up numbers…”, Swee's “illustrative total”) was not in
this assignment. The non-interactive “Life Line → Care for family” trail is part of
the nav work.

Evidence (uncommitted): `test-artifacts/cxui-001-followup/` holds suite logs, the red-phase
log, 1280px and 375px screenshots, heading geometry and 8 axe reports (0 violations).

## CXUI-001-FOLLOWUP2: residual Low items from the G5/G5X re-check of `85f8109`

Status: **Verified** locally by the automated checks below; independent QA (G5) and
designer (G5X) re-verification are still pending. Branch `fix/cxui-001-followup2`
from `85f8109`. Only `retirepilot/s016.html`, S016 browser tests and this document
change. `retirepilot/api.py`, the API response, the dashboard at `/`, preserved
prototypes and the design tree are unchanged.

| Item | Change (`retirepilot/s016.html`) | Proving case/test |
|---|---|---|
| CXUI-FU-D01 | Result copy uses `monthCount()`: “Over 1 month” / “for 1 month”; 2–120 stay “months”. The API `months` value is checked as an integer 1–120 before display; anything else is treated as an unexpected response (“Something went wrong”), so “0 months” can never render. | `cxuifu2-months`, `cxuifu2-months-375` (1, 2, 12, 120 via the real API; 0 refused before any request; forged `months: 0` response; 375px overflow; axe) |
| CXUI-001-F-D01 | After an edit removes the general message, if field errors remain the heading is rewritten to “Please check these answers”; if none remain the summary hides (R-D02 unchanged). Only the edited field's error clears (D03 unchanged). | `cxuifu2-heading`, `cxuifu2-heading-375` (forced general + server-mapped months error, edit cost; forced general + two client errors, edit months; pure network failure still hides; field-only summary unchanged; recovery; axe) |

Interpretation decisions:
- The combined general + field state isn't produced by `showErrors` in normal use, so
  the tests force it the same way the Designer did (inject the general paragraph and
  heading into a field-error summary), then edit a field.
- The months grammar is UI-only; the API still returns the integer `months`.

Both new cases fail against `85f8109` and pass with this change (red-phase log in the
evidence folder). Browser runs used `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js`;
the 4 new axe reports show 0 violations. Evidence (uncommitted): `test-artifacts/cxui-001-followup2/`.
