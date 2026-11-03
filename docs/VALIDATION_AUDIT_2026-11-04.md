# Internal validation audit: 4 November 2026

**Target:** Local RetirePilot v2.6 engineering package. **No remote GitHub CI was run.** This is an internal self-audit, *not* independent financial, security or legal approval.

## Gate verdicts

| Gate | New evidence | Result |
|---|---|---|
| Financial | Existing automated suite 588/588 passes; 9/10 added numeric/adversarial cases pass | **FAIL**: end-age month-proration defect, full CPF/LIFE unverified |
| Security | 4/8 focused probes pass; local encryption and revocation narrowly work | **FAIL for production**: unauthenticated API, spoofable synthetic gate and consent |
| Legal | MAS FAA and PDPC requirements mapped to intended features | **NOT CLEARED**: no qualified written legal opinion, no licence/exemption determination |
| Consumer | 48 in-process synthetic flows work using 3 derived fixture families | **SIMULATED ONLY**: 0/48 real user interviews or observed usability tests |

**Decision: Phase 9 NO-GO, even under a counterfactual assumption that real consumer validation succeeded.**

## P0 financial bug: [#9](https://github.com/eddiepiper/RetirePilot/issues/9)

Synthetic case: person born **1974-05-20**, horizon ends **2027-05-20**. For first five calendar months of 2027, engine reports **S$36,000** earned income; independent calendar-day fraction yields **S$33,212.90** (4 + 19/31 months), a **S$2,787.10 overstatement**. The same clipped-denominator logic affects other partial-month flows; those effects need their own golden tests.

## Security review observations

- `/api/evaluate` accepts anonymous synthetic-profile requests. This is intentional for localhost research, **not safe for real-person data or internet exposure**.
- A profile id starting `RP-SYNTH-` does not guarantee the payload contains no real information; extra person-like fields are accepted.
- Local adult consent method accepts `explicit=True` without authenticated evidence of the consenting adult.
- Local encrypted vault permissions (0600), encrypted content, consent revocation and default-disabled external LLM flag passed limited probes.
- No production auth, tenant isolation, TLS termination, key custody, access-control tests, penetration test or independently approved threat model exists.

## Legal issue-spotting only

- MAS [Guidelines on Provision of Financial Advisory Service](https://www.mas.gov.sg/regulation/guidelines/guidelines-on-provision-of-financial-advisory-service) use a two-stage test: whether activity is advice and whether it is carried on as a business.
- MAS [FA licensing rules](https://www.mas.gov.sg/regulation/capital-markets/apply-for-licensing-or-registration-of-capital-market-entities/financial-advisers) must be assessed if RetirePilot's functions enter regulated financial advisory scope.
- PDPC [data protection obligations](https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Resource-for-Organisation/Data-Protection-Obligations-under-the-PDPA.ashx?la=en) and [AI recommendation guidelines](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/advisory-guidelines/advisory-guidelines-on-the-use-of-personal-data-in-ai-recommendation-and-decision-systems.pdf) require contextual assessment for real financial records, household consent, external AI and retention.
- This audit is **not** a lawyer's opinion or MAS authorisation.

## Consumer assumption

Exactly 48 synthetic derived assessments ran without exceptions, but all were based on only three synthetic fixture families. They do not establish real-user comprehension, accessibility, task completion or user acceptance. If a hypothetical 48 real sessions were all deemed PASS, release still fails the other independent gates.

## Evidence provenance

- Original local v2.6 source archive SHA256: `417aab77bb907a0c00572c3f7cb74afefc18e1650d9fa46d4a11fcd7b3a497e4`
- New reproduction script SHA256: `c1293010131845dac0e3dad2646edf22d86fb7e62592d43ca8570fd6d6ca72d7`
- Output evidence JSON SHA256: `e72ee5c4f1228854cd60f506d8c7d844b2440969f8e699c0bbf2ff6572c568db`
- PDF audit SHA256: `40870569d77a88c7ce0e27d25d9ef7cb74e854722ef343a645bbc316530361e7`

The reproduction script, machine-readable evidence and PDF were produced in this conversation; they are **not part of the GitHub repository** yet. The full v2.6 source migration is also pending. Test claims must not be represented as GitHub Actions results.

**Required closure:** Exact source commit, CI pass, corrected goldens, independent financial/security reviewers and written Singapore-qualified legal scope clearance.