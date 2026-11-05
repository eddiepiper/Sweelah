# RetirePilot

**Singapore-focused retirement and household financial-planning research prototype, primarily for citizens and PRs aged 45+.**

**Engineering version:** v2.7. **External-pilot release decision: NO-GO.** Source-code merge and a passing CI check do not authorise a customer pilot.

## Approved product direction

Product-owner decisions **1A–7A** are recorded in [the decision register](docs/APPROVED_DECISIONS_v2.7.md).

- Provide personalised retirement projections, scenarios and educational explanations, **not regulated product recommendations or automatic transactions**.
- For personal CPF LIFE income, require a **member-provided official estimate**; CPF Board published examples are illustrative only.
- Retain all 96 provisional archetypes without customer-facing confidence percentages.
- Block sharing of another adult's financial information until their identity and separate consent are verifiably established.
- Prioritise five events: housing downsizing, payout timing, part-time retirement, parent care and divorce/family transitions.
- Obtain external qualifications, written scopes and quotations before approving any paid independent reviewer.
- Continue to require **48 actual, consenting research participants** before any external pilot; simulated interviews never count.

## Repository contents

| Path | Contents |
|---|---|
| [retirepilot/](retirepilot/) | Python API, policy references, projections, scenario contracts and local synthetic security components |
| [tests/](tests/) | Synthetic unit/integration and approved-decision checks |
| [data/](data/) | Synthetic-only research fixtures and 46 scenario contracts |
| [docs_release/](docs_release/) | **Original PSD/TSD v2.7 in Word and PDF**, Master Library v1.7, validation reports, evidence ZIP, document index and checksums |
| [docs/](docs/) | Approved decisions, financial/research audits, release-gate tracker and project governance |
| [docs/FINANCIAL_ENGINE_AGE_COVERAGE.md](docs/FINANCIAL_ENGINE_AGE_COVERAGE.md) | F01–F18 age subject, effective-date, evidence and boundary-test requirements for Atlas |
| [scripts/verify_release_documents.py](scripts/verify_release_documents.py) | Reconciles nine release artifacts against exact SHA-256, size and file-format checks |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Source tests, 96-archetype contracts, API smoke checks and release-document integrity |

[Browse the release document index](docs_release/DOCUMENT_INDEX_v2.7.md).

## Financial-engine implementation status

The [18 F01–F18 financial-engine contracts](research/retirepilot_2026_11_04/financial_engine_contracts_18.json) are approved **requirements**, not 18 completed calculations. Existing code provides synthetic cash-flow/projection logic and bounded CPF, tax and housing references. In particular, CPF contribution and interest references are not a lifetime CPF ledger, and personal CPF LIFE payouts must come from a member-provided official estimate. The [age and effective-date coverage matrix](docs/FINANCIAL_ENGINE_AGE_COVERAGE.md) identifies the subject person, trigger date, source evidence, current implementation boundary and required tests for every F01–F18 item. Atlas must use the [implementation handover](research/retirepilot_2026_11_04/ATLAS_HANDOFF_BUSINESS_RULES_v1.8.md) and keep specified, implemented, internally tested and independently verified states separate.

## Run the synthetic test baseline

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python audit/run_rule_contracts_v22.py
python scripts/verify_release_documents.py
# API smoke checks require a localhost uvicorn server; see CI workflow
```

Verified GitHub Actions baseline on the v2.7 review branch: **609/609 Python tests, 498/498 classifier rule checks, 13/13 localhost API checks**, plus release-document integrity verification. These are internally authored synthetic tests, **not independent financial, legal, security or consumer certification**.

## Release gates

See [Release Gates](docs/RELEASE_GATES.md) and [the pre-push gate assessment](docs_release/RetirePilot_PrePush_Gate_Report_2026-11-04.md).

- Full future CPF account, interest and retirement modelling: incomplete.
- The five priority scenarios: four limited previews and one blocked complex family transition, not fully validated engines.
- Production authentication, adult identity and consent: incomplete; no real customer data permitted.
- Independent financial and cybersecurity findings: no qualified external sign-offs.
- Singapore-qualified written legal scope opinion: not obtained.
- Real consumer research: **0/48 completed**.

**Phase 9 remains NO-GO.** Merging into `main` is version-control housekeeping for a research prototype, not a deployment or release approval.


## SweeLah! visual prototypes

The consumer-facing **SweeLah!** design system, six interactive onboarding/dashboard HTML prototypes, Singapore-inspired illustrations, animated assets, and preview screenshots are in [design/sweelah](design/sweelah/README.md). Start with the [latest full journey](design/sweelah/prototypes/SweeLah_Onboarding_and_Dashboard_With_Floating_Clouds.html).

The design is a synthetic-data UI concept and does not alter the RetirePilot financial model, production data controls, or Phase 9 release status.
