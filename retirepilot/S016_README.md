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
The new screen uses 16px body text, dark ink/green tokens, visible keyboard focus
and reduced-motion support rather than the prototype's small/light text.

## API

`POST /api/scenarios/S016/preview` accepts:

```json
{"synthetic_profile_id":"RP-SYNTH-S016","params":{"additional_care_cost_monthly":"1200","months":12}}
```

The only calculation inputs are a positive cost with at most two decimal places
and integer months 1–120. Neither
field defaults or prefills. Fractional months are always refused; positive decimal
costs are accepted up to two places. The UI and endpoint strip leading `S$` and
commas (for example `1,200.5`).
Sub-cent precision is refused before the preview call, with HTTP 422 and no result:
“Enter an amount with up to 2 decimal places, for example 1200.50.”
Precision is checked without float rounding: JSON fractional tokens are parsed as
Decimal for this endpoint, and the UI counts fractional digits using the input
string and an integer exponent. Other endpoints retain their default JSON parser.
Exponent forms are accepted when their expanded Decimal scale has at most two
fractional places: `1e2` = 100, `1e-2` = 0.01, `1.005e2` = 100.50; `1e-3` is refused.
Explicit trailing fractional zeros count: `1.50` is accepted, `1.500` is refused.
`1.005` (string or JSON number) is refused, while `1.50` × 12 displays S$18.00.
The existing preview arithmetic is unchanged.
The synthetic fixture identifier is a local-development guard, not authentication
or permission to process real financial records. Do not expose this server publicly.

The endpoint delegates all validation/arithmetic to `preview_priority_scenario`.
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
The existing `_amount` zero-cost error still says “nonnegative amount required”.
This endpoint maps it to “must be more than 0”; the UI maps errors to plain-language
field messages. Recommended follow-up: correct the shared positive-only wording
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
