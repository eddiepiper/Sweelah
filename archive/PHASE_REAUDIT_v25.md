# RetirePilot Phase 1–8 Evidence Re-audit v2.5

As of 2026-11-04, based on the packaged implementation and local synthetic tests.

| Phase | Verdict | Verified evidence | Missing evidence |
|---|---|---|---|
| 1 taxonomy | DESIGN BASELINE COMPLETE | Excel retains 18 domains and 96 IDs | Population coverage is not empirically exhaustive |
| 2 scored rules | PARTIAL | 96 rules, 225 predicates, documented weights and technical audits | 0 approved weights, 0 independent human labels, no prevalence/fairness validation |
| 3 classification | TECHNICAL PROTOTYPE | All 96 evaluated, classifier contract tests | Novel blind expert-labelled cases, external calibration |
| 4 household records | LOCAL SYNTHETIC PROTOTYPE | Multi-stream data, consent-gated encrypted local storage | Authentication, multi-tenant authorisation, trusted key management, security review |
| 5 financial calculations | PARTIAL | Monthly cash/debt projections, bounded 2026/27 CPF/tax references, 12 scenario operators, expanded published-table tests | Full CPF LIFE/RA, tax circumstances, official results reconciliation, 26 unmapped scenarios |
| 6 financial assistant | RULE-BASED DEMO | Questions, synthetic memory and actions; `simulated_verified` is no longer real verification | Live approved LLM, genuine evidence service, accessible progressive UI, action execution safeguards |
| 7 assurance | NOT COMPLETE | Self-run unit/contract/API tests; source review | All named independent expert and legal/security/QA signoffs |
| 8 consumer validation | NOT EXECUTED | 48-person plan and session protocol | 0/48 real interview sessions; no actual usability data |

**Phase 9: NO-GO.** The code changes fix misleading behaviours but not the major missing evidence. Passing developer-written tests must not be confused with independent validation.

## Newly closed in v2.5

- RP-V25-01: Invalid / mismatched scenario income IDs no longer silently ignored.
- RP-V25-02: `verified_complete=True` cannot be produced by a self-declared synthetic verifier; only `simulated_verified`, with `verified_complete=False`.
- RP-V25-03: Additional independently transcribed published-table numeric anchors added to test suite (self-run, not externally witnessed).

## Highest remaining blockers in order

1. Full official CPF account transition/contribution/CPF LIFE methodology and 2026/27 financial reconciliation.
2. Singapore qualified financial-advice boundary and privacy/legal review.
3. True end-user identity, household-level authorisation, verified action provider, security engineering.
4. Calibrate 96 matching scores against labelled cases; check false positives and fairness.
5. Support and test additional scenario catalogue cases and consumer-first accessible journeys.
6. Actual research interviews with eligible Singaporean participants and observed usability testing.