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
| [scripts/verify_release_documents.py](scripts/verify_release_documents.py) | Reconciles nine release artifacts against exact SHA-256, size and file-format checks |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Source tests, 96-archetype contracts, API smoke checks and release-document integrity |

[Browse the release document index](docs_release/DOCUMENT_INDEX_v2.7.md).

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

## SweeLah product intelligence library (new: 5 November 2026)

The [SweeLah product-library implementation](docs/SWEELAH_PRODUCT_LIBRARY.md) adds an **unapproved discovery library of 99 Singapore products** (49 OCBC accounts/loans/cards and 50 Great Eastern insurance entries), supported by dated official source links. It does **not** claim complete current product eligibility, pricing, premium, coverage or new-business availability.

| Component | Location | Actual status |
|---|---|---|
| Versioned product catalogue | [products_v1.json](product_library/products_v1.json) | 99 research/discovery records; all detailed criteria unverified |
| Sources and review dates | [sources_v1.json](product_library/sources_v1.json) | Official public directories; product policy terms require further checking |
| Candidate eligibility rules | [rules_v1.json](product_library/rules_v1.json) | Four unapproved examples; **never executable by default** |
| Deterministic evaluation / holdings bridge | [product_library.py](retirepilot/product_library.py) | Implemented fail-closed library validation and limited in-memory contract input adapter; not wired into financial forecasts |
| Synthetic regression tests | [test_product_library.py](tests/test_product_library.py) | Included in the existing `pytest -q` CI job |

Use `python -m pytest -q tests/test_product_library.py` to run the new module tests. For synthetic-only inspection, `from retirepilot.product_library import load_registry, evaluate_product`.

**Boundary:** products, customer holdings, deterministic eligibility and financial projections are separate layers. A directory listing is not an approved underwriting rule. Actual insured benefits must come from a customer's verified policy terms; unverified insurance claims are never forecast as cash inflows. CPF and retirement model limitations, privacy controls and **Phase 9 external-pilot NO-GO** remain unchanged. There are still 18 existing financial-engine *contracts*, not 18 independently validated complete engines.
