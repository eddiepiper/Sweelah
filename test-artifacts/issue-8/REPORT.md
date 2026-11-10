# SWEELAH-ISSUE-8: in-house mapping of the 26 formerly unmapped scenarios (Refs #8)

**Status: INTERNAL / UNVALIDATED.** Engineering did this mapping in-house. No external review, domain-expert review or sign-off. Synthetic/public data only. Phase 9 stays NO-GO.

- Worktree: `/workspace/sweelah-issue-8-v2`, branch `feat/issue-8-scenario-mapping-v2` (no upstream), base `origin/main` = `823ef724cdcf5dfada91a895a51baa60fd6c41ec`. This G5-conditions follow-up is one new commit on `edf3caa`. Confirmed 10 Nov 2026 SGT.
- Issue read read-only via the GitHub connector (`gh` on the box is not authenticated). The issue and its comments were treated as data.

## 1. Count found

**26 confirmed.** `data/scenario_contracts_v26.json` has 46 entries: 20 with registry `previous_status=BOUNDED_OPERATOR` and 26 with `previous_status=UNMAPPED` (S005, S006, S012-S015, S019, S020, S022, S025-S027, S029-S033, S035, S038-S044, S046). That matches the issue and `docs/SCENARIO_MAPPING_v2.6.md`. The coverage matrix records those 20 bounded entries as `implemented: PREEXISTING_BOUNDED_OPERATOR`; that is the matrix's implemented value, not a second registry status.

Discrepancies to note:
1. v2.6 already gave these 26 a runtime *contract* (`MAPPED_TO_EXPLICIT_CONTRACT_NOT_PRODUCTION_READY`). Seven have limited converters and 19 fail closed. What was still missing was what the issue asks for: semantic scope, engines, required facts, timing, missing-data handling, conflict checks, and a coverage matrix that separates mapped / implemented / golden-tested / domain-approved. That is what this change adds.
2. The issue says the 20 pre-existing entries map to "12 bounded operators". They actually use **11** distinct operators (`core.ALLOWED_SCENARIO` defines 13; `one_time_windfall` and `housing_payment_shock` are not used by the 20). This is informational only and nothing was changed.
3. S020, S030 and S012 are `NOT_SAFE_TO_COMPILE` in v2.6 but have v2.7 priority previews (decision 5A). They are classed as LIMITED_PREVIEW / BLOCKED_PREVIEW, not as fail-closed.

## 2. Method

- **Schema / conventions.** The new records carry the v2.6 registry's `id`, name, category and `execution_strategy` (as `v26_*`, cross-checked against the registry), plus `previous_status: UNMAPPED`. New fields: `mapping_status: MAPPED_INTERNAL`, **`validation_status: INTERNAL_UNVALIDATED`**, `external_validation: false`, `mapped_by: "Engineering Lead (in-house)"`, `coverage{mapped, implemented, golden_tested, domain_approved}`, `component_tests` and `rationale`. No existing status field could express "internal/unvalidated", so `validation_status` was added.
- **Overlay, not an edit.** The mapping is stored separately in `data/scenario_mapping_internal_issue8.json`. `data/scenario_contracts_v26.json` is hash-pinned in `docs_v26/VERIFICATION_MANIFEST_v26.json` and is **unchanged**, and a test asserts its hash.
- **Sources.** Semantic scope, engines (F01-F18), required facts and guardrail are copied verbatim from `research/retirepilot_2026_11_04/scenario_engine_contracts_46.json`. `test_mapping_follows_research_contract_and_registry` pins all four fields to that contract, including `semantic_scope` against `Event and calculation rule`. `reference_errors()` also checks required facts and guardrails against the same contract. The runtime level comes from the v2.6 registry and `priority_scenarios_v27.PRIORITY_STATUS`. Applicable decisions come from engine overlap with `APPROVED_PRODUCT_DECISIONS_D08_D16.json` "Affected engines"; D11 is limited to S020 and D16 applies to all. Timing rule, missing-data behaviour, incompatible_with and rationale are **Engineering's own judgement**.
- **Reproducible.** `scripts/build_internal_scenario_mapping_issue8.py` regenerates the JSON. Output is deterministic (sha256 identical across reruns).
- **No runtime change.** `retirepilot/scenario_mapping_internal.py` is read-only metadata: `internal_mapping()`, `coverage_matrix()` and `reference_errors()`. Nothing in the API, service or UI imports it.

## 3. Mapping table (26)

| ID | Event | Runtime level | Engines | Decisions | Conflicts | Label | Rationale |
|---|---|---|---|---|---|---|---|
| S005 | Delayed retirement | `LIMITED_COMPONENT` | F02, F03, F06, F14 | D08, D09, D10, D16 | S029 | `INTERNAL_UNVALIDATED` | Existing RETIREMENT_GOAL_ONLY converter moves the stop-work age only; full mapping adds F03/F06 CPF accrual, which is not implemented, so coverage stays a limited component. |
| S006 | Return to work | `NOT_IMPLEMENTED_FAIL_CLOSED` | F02, F03, F04, F05, F07 | D08, D16 | S033, S046 | `INTERNAL_UNVALIDATED` | Needs a new dated income stream plus employee/SEP/platform CPF recalculation (F03-F05); no safe component subset exists, so it stays fail-closed. |
| S012 | Divorce | `BLOCKED_PREVIEW` | F01, F02, F08, F12, F18 | D12, D15, D16 | S013 | `INTERNAL_UNVALIDATED` | Priority 5A item whose v2.7 entry deliberately always blocks; mapping to F01/F12/F18 records the facts a future engine needs without implying any effect. |
| S013 | Widowhood | `NOT_IMPLEMENTED_FAIL_CLOSED` | F01, F02, F07, F11, F18 | D12, D15, D16 | S012 | `INTERNAL_UNVALIDATED` | Requires verified survivor income, claims and estate data across F07/F11/F18; nothing can be computed from defaults, so fail-closed. |
| S014 | New child/dependant | `LIMITED_COMPONENT` | F02, F12, F17 | D12, D16 | - | `INTERNAL_UNVALIDATED` | Cost-only recurring component already exists; benefits/grants (F17) stay excluded from baseline per D12, so it remains a limited component. |
| S015 | Adult child support | `LIMITED_COMPONENT` | F02, F12, F14 | D09, D10, D16 | S044 | `INTERNAL_UNVALIDATED` | Recurring-cost component covers cash support; incompatible with S044 for the same transfer to avoid double counting (D16). |
| S019 | Property-value decline | `NOT_IMPLEMENTED_FAIL_CLOSED` | F08, F14, F16 | D09, D10, D14, D15, D16 | S020, S022 | `INTERNAL_UNVALIDATED` | A net-worth/LTV change, not a cash outflow; the current projection has no per-property equity ledger (F08), so it fails closed. |
| S020 | Downsizing | `LIMITED_PREVIEW` | F08, F06, F02, F14 | D08, D09, D10, D11, D16 | S019, S022 | `INTERNAL_UNVALIDATED` | Priority 5A item with a v2.7 cash-arithmetic preview that may not post to the projection; the full F08/F06 waterfall is not implemented. |
| S022 | Lease monetisation | `NOT_IMPLEMENTED_FAIL_CLOSED` | F08, F06, F07, F14 | D08, D09, D10, D16 | S020, S019 | `INTERNAL_UNVALIDATED` | Depends on official HDB eligibility and quote; no estimate is permitted, so it fails closed. |
| S025 | Low real returns | `NOT_IMPLEMENTED_FAIL_CLOSED` | F10, F14, F16 | D09, D10, D14, D15, D16 | S024, S026, S028 | `INTERNAL_UNVALIDATED` | Needs per-asset return and inflation paths (F10); a global override would double-subtract inflation alongside S028, so it fails closed. |
| S026 | Poor early withdrawal returns | `NOT_IMPLEMENTED_FAIL_CLOSED` | F10, F14, F16 | D09, D10, D14, D15, D16 | S024, S025 | `INTERNAL_UNVALIDATED` | Sequence-of-returns risk requires a time-indexed portfolio path (F10/F14) that does not exist yet; fail-closed. |
| S027 | Concentrated stock loss | `NOT_IMPLEMENTED_FAIL_CLOSED` | F10, F14, F16 | D09, D10, D14, D15, D16 | S024 | `INTERNAL_UNVALIDATED` | Needs holding-level portfolio detail; reusing market_crash would wrongly shock the whole portfolio, so it fails closed. |
| S029 | Earlier retirement | `LIMITED_COMPONENT` | F02, F03, F06, F07, F14 | D08, D09, D10, D16 | S005 | `INTERNAL_UNVALIDATED` | Existing converter moves the stop-work age only; liquidity bridge (F14) and CPF effects (F03/F06/F07) are not implemented, so limited component. |
| S030 | Payout deferral | `LIMITED_PREVIEW` | F07, F14, F16 | D09, D10, D14, D15, D16 | S032 | `INTERNAL_UNVALIDATED` | Priority 5A item with a v2.7 comparison-only preview; no actuarial or lifetime calculation, so limited preview. |
| S031 | Voluntary top-up | `NOT_IMPLEMENTED_FAIL_CLOSED` | F06, F07, F14 | D08, D09, D10, D16 | - | `INTERNAL_UNVALIDATED` | Needs verified RA limits and account transfers on the F06 ledger plus a fresh F07 estimate; fail-closed. |
| S032 | Pre-payout funding bridge | `NOT_IMPLEMENTED_FAIL_CLOSED` | F07, F14 | D09, D10, D16 | S030 | `INTERNAL_UNVALIDATED` | Needs dated cash drawdown and reserve logic (F14, D09); restricted CPF can never fill the gap, so fail-closed until built. |
| S033 | Contribution interruption | `NOT_IMPLEMENTED_FAIL_CLOSED` | F02, F03, F04, F05, F06 | D08, D16 | S006 | `INTERNAL_UNVALIDATED` | Needs contributor-specific CPF posting and allocation (F03-F06); never assume contributions continue, so fail-closed. |
| S035 | Disability-related cost shock | `LIMITED_COMPONENT` | F02, F11, F12, F14 | D09, D10, D12, D16 | S036 | `INTERNAL_UNVALIDATED` | Cost component exists; income disruption (F02) and benefits (F11/F17) are separate and unimplemented; overlapping S036 care cost would double count. |
| S038 | Retire overseas | `NOT_IMPLEMENTED_FAIL_CLOSED` | F09, F13, F14, F15 | D09, D10, D13, D16 | S040 | `INTERNAL_UNVALIDATED` | Cross-border tax, healthcare, residency and FX (F09/F13/F15) are unsupported, so fail-closed. |
| S039 | Exchange-rate movement | `NOT_IMPLEMENTED_FAIL_CLOSED` | F10, F13, F14, F15 | D09, D10, D13, D16 | - | `INTERNAL_UNVALIDATED` | Needs explicit currency amounts and dated FX rates (F15); fail-closed. |
| S040 | Repatriation | `NOT_IMPLEMENTED_FAIL_CLOSED` | F09, F13, F14, F15 | D09, D10, D13, D16 | S038 | `INTERNAL_UNVALIDATED` | Cross-border law and verified flows required; fail-closed. |
| S041 | Foreign pension change | `NOT_IMPLEMENTED_FAIL_CLOSED` | F09, F13, F15 | D13, D16 | - | `INTERNAL_UNVALIDATED` | Needs verified foreign pension terms with FX and withholding (F13/F15); fail-closed. |
| S042 | Inheritance | `LIMITED_COMPONENT` | F13, F14, F18 | D09, D10, D12, D16 | - | `INTERNAL_UNVALIDATED` | Net cash receipt component exists; entitlement, probate and tax are out of scope, so limited component. |
| S043 | Business sale | `NOT_IMPLEMENTED_FAIL_CLOSED` | F02, F09, F13, F14, F18 | D09, D10, D12, D16 | S046 | `INTERNAL_UNVALIDATED` | Needs net proceeds, liabilities and earnings cessation (F02/F09/F18); avoid double counting value and proceeds, so fail-closed. |
| S044 | Major gift to children | `LIMITED_COMPONENT` | F14, F18 | D09, D10, D12, D16 | S015 | `INTERNAL_UNVALIDATED` | Cash gift outflow component exists; recipient-household effects only when ownership is known, so limited component. |
| S046 | Business failure | `NOT_IMPLEMENTED_FAIL_CLOSED` | F02, F09, F13, F14, F18 | D09, D10, D12, D16 | S043, S006 | `INTERNAL_UNVALIDATED` | Liabilities, guarantees and income must be documented together (F02/F18); fail-closed. |

Coverage matrix over all 46 entries (`coverage_matrix()`): mapped **46/46**. Implemented: `PREEXISTING_BOUNDED_OPERATOR` 20 (for the 20 registry entries whose `previous_status` is `BOUNDED_OPERATOR`), LIMITED_COMPONENT 7, LIMITED_PREVIEW 2, BLOCKED_PREVIEW 1, NOT_IMPLEMENTED_FAIL_CLOSED 16. golden_tested **0**, domain_approved **0**. Mapped does not mean implemented, and unsupported entries still refuse.

## 4. Tests

File: `tests/test_scenario_mapping_internal_issue8.py`, **78 tests** (the original 77 plus `test_reference_checker_detects_mismatched_and_dangling_facts_and_guardrails`). They check:
- the count is 26 of 46
- all 46 entries are mapped
- the mapping covers exactly the 26
- the document-level label
- each of the 26 entries carries `INTERNAL_UNVALIDATED`, `external_validation=false`, `golden_tested=false`, `domain_approved=false` and a rationale
- no dangling references (`reference_errors()==[]`), covering v26 IDs, names, categories and strategies, F-engine IDs, D-decision IDs, incompatible_with IDs, v2.7 preview IDs, `component_tests` node references resolved by AST, and required facts and guardrails against the research contract
- the checker itself flags each kind of dangling reference, including a dangling required fact, a missing required fact, a mismatched guardrail, and a dangling guardrail
- the mapping matches the research contract on `semantic_scope` (`Event and calculation rule`), engines, required facts and guardrail
- the 16 fail-closed entries still raise in `compile_catalog_scenario`
- the coverage-matrix counts
- the mapping text makes no validation claims
- the v26 registry hash is unchanged

Semantic-scope pin (G5 condition 1): `semantic_scope` is asserted in `test_mapping_follows_research_contract_and_registry`. To show the red result, S025's `semantic_scope` was temporarily changed to a non-contract string, the tests were run, and the JSON was restored with `git checkout`. The mutated text made `test_mapping_follows_research_contract_and_registry[S025]` fail; the other 25 parametrized cases passed, and the full issue-8 file was **1 failed, 77 passed**. After restore, S025 passed again.

| Phase | Result | Log |
|---|---|---|
| Red (S025 `semantic_scope` mutated, then restored) | Contract test: **1 failed, 25 passed**. Full issue-8 file: **1 failed, 77 passed** | `semantic-scope-pin-red.log` |
| Green targeted | **78 passed** | `green-phase-targeted.log` |

Full suites, run with `/workspace/sweelah-baseline-venv` after the pin was restored (10 Nov 2026, 9:47pm SGT):

| Suite | Result | Log |
|---|---|---|
| `pytest -q -rs` (full) | **899 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning (starlette/anyio). That is 821 existing + 78 new | `pytest.log` |
| Rules `audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** (needs `PYTHONPATH=.`; without it the script raises ModuleNotFoundError, an environment issue that is also present on main) | `rules.log`, `rules-no-pythonpath.log` |
| Browser `tests/test_s016_browser.py -v -s` (Chromium), `AXE_CORE_PATH=/tmp/cxui-axe/node_modules/axe-core/axe.min.js` | **46 passed**. Counts from this log: `grep -c PASSED browser.log` = 46 (matches the pytest summary). `grep -cw PASS` = 47 because the accessibility case also prints `axe WCAG checks PASS` when axe-core is available. `grep -c PASS` = 93 (46 `PASSED` lines + 46 `PASS S016 browser ...` lines + the one axe line). The earlier "71 PASS lines" figure was wrong. | `browser.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace; host previews 8769-8773 untouched) | **PASS 20/20** | `api.log` |
| Release `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

The pre-existing manifest pin mismatches for `retirepilot/core.py`, `retirepilot/projection_v22.py` and the research integrity pin for `ATLAS_HANDOFF_BUSINESS_RULES_v1.8.md` are unchanged and are not part of this commit. They did not fail this pytest run (same as on main).

Exit codes: `exits.txt`. Environment: `env.txt`.

## 5. Visible UI change: **No**

No HTML, CSS, JS, API route or service code changed. The new module is not imported by `api.py`, `service.py`, `ui.html` or `s016.html`. The v2.6 registry and the v2.7 previews are byte-identical, so every response and page renders as before. **G5X should not be needed.**

## 6. Residual risks

1. **Unvalidated judgement.** Timing rules, missing-data behaviour, conflict pairs and rationales are in-house opinions. Nobody has checked them against CPF Board, HDB or IRAS rules or legal advice. They must not be read as domain-approved.
2. **Conflicts are declared, not enforced.** `incompatible_with` records double-count and ordering risks (D16), but no runtime composition check enforces them yet.
3. **Decision mapping is mechanical.** Engine overlap can be over-inclusive (for example D14/D15 attach to every F16 entry). Review it before using it as a requirement list.
4. **The research source is synthetic.** Engines, facts and guardrails come from synthetic research contracts marked "specified, not validated".
5. **Component tests are self-run.** They are not independent golden references, which is why `golden_tested` is false everywhere.
6. **Issue #8 must stay OPEN.** Implementation, golden tests and external validation for the 26 are still outstanding.
