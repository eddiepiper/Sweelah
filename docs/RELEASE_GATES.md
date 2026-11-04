# RetirePilot v2.7: Release Gates

**Last source-control review:** 2026-11-04.  
**Pilot status:** **NO-GO**. No real customer data or external deployment until all appropriate release gates are passed and approvals documented.

| Gate | Required evidence | Verified state |
|---|---|---|
| G1 Source and documentation integrity | Complete v2.7 source and original PSD/TSD/Excel files committed, fixed dependency versions, repeatable checks, successful GitHub CI and SHA-256 manifest | **PASS for engineering baseline** (PR #10 CI). Reconfirm on `main` post-merge |
| G2 Persona quality | Independent calibration labels for 96 archetypes, agreed errors/thresholds and fairness review | **OPEN**: provisional descriptors only |
| G3 Financial correctness | Independently reconciled 2026/27 CPF, housing, tax and retirement golden cases; missing-data refusal | **OPEN**: bounded modelling only, external reviewer outstanding |
| G4 Household privacy and security | Production auth, individual adult consent and household permissions, key custody, privacy threat model, security testing | **OPEN**: synthetic-only local protection and denied sharing |
| G5 Assistant safety | Safe explanation/approval state machine; action verification and correct error handling | **OPEN**: demonstration states are synthetic, no production actions |
| G6 Professional assurance | Independent finance/QA/security assessment and qualified Singapore financial-regulatory/privacy legal advice | **OPEN**: four exploratory enquiries, no signed professional findings |
| G7 Consumer acceptance | 48 real observed studies with recorded comprehension, accessibility and correction evidence | **OPEN**: 0/48 real sessions |
| G8 External pilot authorisation | Named owner GO decision, acceptance of residual risk, operations and rollback | **BLOCKED** by G2–G7 |

## Approved product-owner decisions

[1A–7A](APPROVED_DECISIONS_v2.7.md): educational planning, member-provided official CPF LIFE estimates, provisional no-score personas, independently verified adult consent, staged five-scenario development, reviewer quotes before appointments, and a mandatory real 48-participant research gate.

## Technical evidence, scope and limits

- [Final pre-push assessment](../docs_release/RetirePilot_PrePush_Gate_Report_2026-11-04.pdf), [text version](../docs_release/RetirePilot_PrePush_Gate_Report_2026-11-04.md).
- [Original v2.7 PSD, TSD and workbook](../docs_release/DOCUMENT_INDEX_v2.7.md), with exact SHA-256 checksums in [manifest](../docs_release/BINARY_DOCUMENT_MANIFEST_v2.7.json).
- [GitHub Actions CI](../.github/workflows/ci.yml) verifies 609 Python tests, 498 internal rule contracts, 13 synthetic API checks and release-document integrity.
- The P0 partial-final-month bug has an internally passing correction, but [Issue #9](../../issues/9) remains open pending independent financial validation.
- [Issue #1](../../issues/1) tracks source migration, eligible for closure only after `main` verification.

**Passing G1 is not sufficient to authorise a pilot.** No independent professional, legal, security or real consumer approvals are implied by these documents.

## Next release priorities

1. Independently reconcile CPF, retirement, tax and event forecasts; complete missing lifetime CPF logic.
2. Complete the five highest-value scenario engines and corresponding goldens.
3. Integrate real household identity and consent, threat modelling, negative tests, private secrets and secure deployment.
4. Obtain written external scopes, qualifications, quotes and permission to engage independent experts.
5. Recruit 48 real adults and complete observed research and remediation.
6. Obtain an explicit, evidence-backed GO/NO-GO decision before pilot.
