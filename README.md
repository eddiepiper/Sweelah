# RetirePilot

**Singapore-first personal and household retirement planning research prototype (age 45+).**

> **Project status (2026-11-04): v2.5 research prototype, synthetic data only. Phase 9 external pilot: NO-GO.**

RetirePilot explores ongoing household financial planning across salaried employment, self-employment, commission income, platform work, dependants, housing, CPF and retirement transitions. The working prototype and supporting documents were developed outside this new repository. **This repository is being established as the source of truth for status, risks and future controlled code imports.** It is not yet a deployed application.

## Current evidence (local, self-run, not independent certification)

| Area | Evidence | Qualification |
|---|---|---|
| Persona taxonomy | 18 dimensions, 96 baseline archetypes | Coverage not population-validated |
| Classifier | Evaluates all 96; 498/498 rule-contract checks passed | 0 independent labels; weights uncalibrated |
| Python tests | 477/477 passed on v2.5 extracted package | Self-authored synthetic tests |
| API checks | 13/13 local checks passed | Localhost synthetic prototype |
| Financial engine | Monthly projection, bounded CPF/tax references, 12 scenario operators | Full statutory reconciliation and 26 catalogue mappings outstanding |
| Household data | Consent-gated encrypted *local* synthetic vault | No production identity, key management or multitenant controls |
| Assistant | Guided rule-based workflow, synthetic memory and action states | No live approved AI or authenticated verification |
| Independent reviews | None signed off | Financial, QA, security, privacy and legal gates open |
| Consumer research | 0/48 interviews | Research plan exists, no actual sessions |

**Important:** v2.5 uses `simulated_verified` with `verified_complete=false` in its action demonstration. Synthetic task evidence does not represent real-world completion. Historical v2.4 material is superseded on this point.

## Status and next work

- [Progress report](docs/PROGRESS_v2.5.md)
- [Release gates](docs/RELEASE_GATES.md)
- [Full source migration handover and pending push](docs/FULL_SOURCE_IMPORT_RUNBOOK.md)
- [Security and data-handling boundaries](SECURITY.md)
- GitHub Issues track the outstanding work. No issue should be closed without reproducible evidence.

## Source availability

The complete v2.5 executable package is retained in the original development handover. **Source files are not yet imported to this repository.** Do not infer that a passing test result is a GitHub CI run. The first engineering issue is to import the audited source and establish reproducible CI while excluding personal data, secrets and development artefacts.

## Working principles

- Synthetic financial data only until the appropriate external assurance gates pass.
- Effective-dated, source-linked Singapore policy references and explicit unsupported-case behaviour.
- User-provided CPF LIFE estimates are not replaced with invented payouts.
- Advisory and regulatory scope requires qualified assessment.
- No financial transactions or unsupervised real-world action execution.
- No claims of independent review until named reviewers provide signed evidence.
