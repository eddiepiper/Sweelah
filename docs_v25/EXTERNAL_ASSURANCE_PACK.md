# RetirePilot Independent Assurance Assignment Pack v2.5

**Purpose:** Independent examination of the implemented financial, privacy, security, accessibility and regulatory claims. This is a request for review, NOT evidence of review.

## Materials to supply to reviewers

- Complete tested ZIP and immutable SHA-256 manifest.
- `retirepilot/financial_references_v24.py` and `retirepilot/statutory_2026.py` (source-based bounded calculations).
- `retirepilot/core.py`, `retirepilot/projection_v22.py`, and `data/*.json` (financial model and synthetic profiles).
- `retirepilot/classifier_legacy.py`, `retirepilot/retirepilot_rules_v1.2.json`, and Excel v1.6 (persona gates/weights).
- `retirepilot/local_vault_v24.py`, `retirepilot/planner_session_v24.py`, `retirepilot/llm_adapter.py` (data/privacy/assistant surfaces).
- Reproducible pytest, rule-contract and API results, plus documented open defects.

## Required reviewers and signed outputs

| Independent reviewer | Required work | Minimum signed evidence | Gate |
|---|---|---|---|
| Singapore CPF/retirement specialist | Reconcile age, wage, PR, platform, SEP, OA/RA/MA allocation, housing, payout assumptions | Own golden input/output vectors, official comparator, dated signed variance log | P5-finance |
| Singapore tax expert | Reconcile wages/commission/rental income, deductions, reliefs, YA, tax payments | Independent taxable-income cases, excluded-case map and dated signed review | P5-tax |
| Security professional / privacy officer | Threat model end-user identity, vault, consent, access, encryption, backups, deletion and incident response | Severity-ranked findings, remediation retests, signed DPO/security decision | P4-security |
| Singapore-qualified legal/compliance specialist | Scope the financial-advice regulatory perimeter; suitability, recordkeeping, disclaimers, referral | Signed advice-perimeter matrix and approved prohibited/allowed-function policy | P6-legal |
| Independent QA + accessibility reviewer | Run novel blind persona cases, API abuse tests, keyboard/screen-reader/mobile sessions | Distinct reviewer identity, dated results, raw evidence and failure tracking | P7-QA |

## Review principles

1. Reviewers must not treat developer-written tests as independent reconciliation.
2. Testing a calculation on a synthetic fixture is not government approval, financial advice authorisation or a statistical validation of 96 archetypes.
3. Before pilot, all P0/P1 issues require re-test evidence and explicit risk-owner disposition.
4. The current `simulated_verified` status cannot be presented to users as an action that was genuinely verified.
5. No full live account integration or real-user data collection is authorised by this package.

## Signature record (blank, no approvals received)

`Reviewer name | Qualification | Organisation | Scope & versions reviewed | Findings | Decision | Signature | Date`.

**Current signed reviews obtained:** 0.
