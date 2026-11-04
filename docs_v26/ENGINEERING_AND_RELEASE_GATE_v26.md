# RetirePilot v2.6: CPF and Scenario Engineering Gate

**As of 2026-11-04. Status: research prototype, synthetic-only. Phase 9: NO-GO.**

## Actual code changes

- Added `retirepilot/cpf_retirement_v26.py` with 2026/2027 **exact-55th-birthday** Retirement Account snapshot transitions. Applies SA first then OA up to relevant FRS, closes SA, routes excess SA savings to OA. It rejects non-exact dates, prior RA balances, unconfirmed CPF membership, property pledges, and unsupported cohorts. **Not a complete RA or CPF contributions model.**
- Added a six-row **exact published-example lookup** for male 2026 CPF LIFE Standard Plan, at age 65 or 70. All other amounts, plans and personal payout requests are explicitly rejected; no interpolation or actuarial calculation.
- Added `one_time_windfall` for *confirmed net cash receipts only*. No claims about inheritance, probate, tax, business sales or official entitlements.
- Added `retirepilot/catalog_scenarios_v26.py`, `data/scenario_contracts_v26.json` with exactly 46 contracts: 20 pre-existing bounded mappings and 26 previously unmapped rows now assigned explicit strategies and inputs. Of the 26, seven have **limited** converters, 19 intentionally fail closed.

## Evidence

- 588/588 local automated tests, including 111 additional scenario/CPF tests.
- 498/498 legacy classifier contract checks. Self-generated fixtures, *not independent calibration*.
- 13/13 API smoke checks, and synthetic action demo still indicates `simulated_verified` / no financial execution.
- Tests self-run locally against synthetic profiles. **No GitHub CI, external financial certification or production test performed in this change.**

## Mandatory independent review

1. Singapore financial planning SME/CFP: review CPF transitions, tax, claims and limitations with independent oracles.
2. Independent security firm: review threats, identity, consent, tenancy, storage, secrets and future deployed build.
3. Singapore legal counsel: financial advice regulation, CPF/benefits communications, PDPA and research pilot conditions.
4. Independent QA: rerun on reviewed source commit, perform adversarial tests and browser accessibility verification.
5. Research recruiter: recruit 48 consented participants; zero confirmed now.

## Critical missing modules

- All-cohort future CPF salary/SEP/platform contribution projections, allocations, monthly interest credit and caps.
- Retirement Account, SA closure for older cohorts with real statements and property commitments.
- CPF LIFE plan options, personal actual payouts, premium allocation and non-Standard plans.
- Income tax actual liability and relevant reliefs; HDB proceeds/eligibility.
- Nineteen scenario-specific full financial/life-event engines; seven limited converters are **not** complete semantics.
- Independent approvals, user authentication, secure multi-tenancy, and actual field research.

## Official sources

- https://www.cpf.gov.sg/service/article/what-happens-to-my-cpf-savings-when-i-turn-55
- https://www.cpf.gov.sg/service/article/what-is-the-closure-of-special-account-for-members-aged-55-and-above-about
- https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum
- https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month
- https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates

**Decision:** Further internal research is GO. Real financial records, public pilot and personalised financial advice remain NO-GO.
