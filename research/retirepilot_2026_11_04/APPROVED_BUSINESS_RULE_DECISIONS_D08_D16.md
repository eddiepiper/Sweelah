# RetirePilot: Nine Approved Business-Rule Decisions (D08-D16)

**Approval:** Product owner, 4 November 2026
**Scope:** Business logic for Atlas handover; no code changes or claims of external financial validation.
**Status:** All nine recommendations approved unchanged.

| Decision | Rule approved | Acceptance and boundaries |
|---|---|---|
| **D08: Future CPF statutory assumptions** | For unpublished 2028+ policy, continue last published rates solely as optional labelled planning assumptions; user may select an alternative explicit scenario. Never present assumptions as future law. | Model-specific projection years must carry source-year, assumption label, and effective-date override. Fail closed for a requested verified 2028+ figure. |
| **D09: Shortfall funding** | Fund deficits from accessible cash above a user-defined reserve, then user-selected liquid assets; no auto-sale, implicit borrowing or prohibited CPF withdrawals. | If reserve unknown ask for reserve amount or clearly display unallocated gap; preserve account ownership and withdrawal constraints. |
| **D10: Planning horizons** | Present alternative longevity horizons to ages 90, 95 and 100, not a life expectancy prediction. | Show cash runway and shortfall for each horizon and indicate that longevity is a scenario assumption. |
| **D11: Housing downsizing** | Do not label a downsizing path affordable without a documented replacement-property financing and dated settlement plan. | Apply sale price less outstanding mortgage, sale costs and eligible CPF refunds; track cash and CPF recredit separately; show financing gap if unknown. |
| **D12: Unverified entitlements** | Exclude unverified insurance reimbursement, subsidies and inheritance from baseline. Permit a separate conditional upside scenario explicitly labelled unconfirmed. | Evidence date, ownership, eligibility and receipt timing required to promote a cash flow to baseline. |
| **D13: Overseas retirement** | Until the jurisdiction-specific retirement model is verified, limit cross-border analysis to documented cash flows and dated FX assumptions. | No claim about foreign tax, healthcare eligibility, residence or scheme rights without verified country-specific evidence. |
| **D14: Readiness language** | Show cash runway, goal shortfall, assumptions and sensitivity, not artificial confidence scores or uncalibrated persona percentages. | Consumer-facing result must omit all numeric persona match scores; internal QA can retain them. |
| **D15: Missing spouse data** | With missing or withheld household consent, calculate using only confirmed individual-owned facts and label the remaining household position unknown. | No implied zero for unknown and no spouse CPF/income/asset guesses. |
| **D16: Compound scenarios** | Compose multi-event scenarios through dated, owner-specific transaction and state ledgers with deterministic precedence and conflict warnings, preventing double counting. | Detect duplicated cash shocks, conflicting asset states and overlapping benefit/income adjustments; refuse unresolved collisions. |

## Version and validation boundaries

- The 18 financial-engine and 46 scenario contracts are *design specifications*, not a demonstration that the engines have been implemented or externally reconciled.
- The 48 consumer roleplays and walkthrough JSON describe **fictional synthetic** persons. They are not 48 real interviews; actual participant research remains **0/48**.
- Prior D08-D16 'open' decisions in the original readout are preserved as a historical snapshot. This approval register supersedes their decision status.
- Security engineering and legal clearance were excluded from the specific consumer tabletop exercise. These remain independent release gates and have not been waived.
- CPF statutory inputs require official dated sources, numeric golden cases and exception coverage before Atlas can consider a financial engine accepted.
- Do not silently use unknown or unverified inputs as zero, count unconfirmed benefits in baseline, or claim an illustrative CPF LIFE example is a personal estimate.

## Atlas acceptance handover

1. Read this decision register and financial_engine_contracts_18.json and scenario_engine_contracts_46.json as the requirements baseline.
2. Implement each contract with input schema, ownership, effective dates, calculation behaviour, exceptions, output provenance and tests.
3. Cross-check the source-year CPF/tax policy tables against dated official sources before engine tests; use member-supplied official CPF LIFE estimates only.
4. Treat roleplay scripts as design challenges. For protective refusals verify correct non-fabrication, not numerical outputs.
5. Publish a coverage matrix that distinguishes documented, implemented, internally tested, independently validated and blocked.

**Decision status:** APPROVED FOR ATLAS REQUIREMENT HANDOVER. **Financial correctness:** NOT CERTIFIED. **Real consumer study:** NOT EXECUTED. **Pilot:** NO-GO.
