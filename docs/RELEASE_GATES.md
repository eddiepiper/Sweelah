# RetirePilot Release Gates (as of 2026-11-04)

**No external pilot until all P0 gates pass.** Design artefacts, test counts and prepared checklists are not sign-offs.

| Gate | Acceptance evidence | Current verdict |
|---|---|---|
| G1 Source integrity | v2.5 source, locked dependency policy, clean CI, hashes and repeatable scripts | OPEN: import pending |
| G2 Persona quality | Independent labels across 96 archetypes, agreed thresholds, fairness and false-positive assessment | OPEN |
| G3 Financial correctness | Official 2026/27 Singapore CPF, tax, housing and retirement golden cases independently reconciled, missing-data refusal tests | OPEN |
| G4 Household privacy | Threat model, authentication, household consent/role model, keys, encryption, deletion and red-team evidence | OPEN |
| G5 Assistant safety | Grounded explanation, approval state machine, verified actions, privacy boundaries and human escalation; real testing | OPEN |
| G6 Professional assurance | Named financial SME, independent QA/security specialists, PDPA/privacy assessment, qualified Singapore financial-advice legal review | OPEN |
| G7 Consumer validation | 48 planned sessions actually observed, transcribed, analysed with demographics, accessibility and comprehension thresholds | OPEN |
| G8 Pilot authorisation | Signed owner decision relying on G1–G7, documented risk acceptance and rollback plan | BLOCKED |

## Highest-priority backlog

1. Import actual v2.5 package into the private repository with reviewed file exclusions.
2. Establish unit/contract/API CI using synthetic fixtures only.
3. Produce complete CPF account, RA and CPF LIFE reference methodology; reconcile against official examples.
4. Expand scenario coverage with independently specified reference cases.
5. Review calibration and scoring with a blinded, separately labelled cohort.
6. Implement authenticated household permissions, production key custody and consent lifecycle.
7. Replace simulated action verification with approved third-party verification or keep action as unverified.
8. Carry out independent finance, security, regulatory and QA review.
9. Recruit and test real Singaporean participants age 45+.

## Decision control

Do not mark any gate PASS solely on the basis of an assistant-generated checklist or self-authored tests. Record who reviewed what, against which exact commit and evidence, on which date.


## Product-owner approved v2.7 decisions (2026-11-04)

See [APPROVED_DECISIONS_v2.7.md](APPROVED_DECISIONS_v2.7.md) and [ENGINEERING_REMEDIATION_v2.7.md](ENGINEERING_REMEDIATION_v2.7.md).

Approved: **1A** educational financial planning only; **2A** member-provided official CPF LIFE estimates; **3A** provisional descriptions of all 96 personas with no numerical confidence claims; **4A** independently verified adult identity and consent before sharing; **5A** five priority scenarios before the remainder; **6A** obtain proposals and quotations before any appointment; **7A** assume consumer PASS only for planning, never as completed real research.

**Local P0 correction:** terminal partial-month proration has been repaired in the v2.7 local source and passed independent arithmetic checks, but GitHub Issue #9 remains OPEN pending source migration and CI. The consumer-facing persona display and CPF LIFE provenance guard were updated locally. Household sharing remains fail-closed and unauthenticated identity remains unintegrated.

**Source-of-truth qualification:** As of 2026-11-04, v2.7 is a **local 77-file engineering handover**, not a confirmed GitHub main-branch implementation. 609/609 pytest, 498/498 internal rule checks and 13/13 existing API checks are **local self-run**. GitHub CI remains unverified.

No gate is closed solely by these code changes; all independent financial, security, legal and real 48-participant research gates remain OPEN. **Phase 9 remains NO-GO.**
