# RETIREPILOT | FINAL PRE-PUSH GATE REPORT

**As of 4 November 2026 | Private repo:** https://github.com/eddiepiper/RetirePilot  
**Source review:** PR #10, https://github.com/eddiepiper/RetirePilot/pull/10  
**Review basis:** V2.7 local synthetic source, code inspection, local verification and GitHub CI metadata.  
**Decision:** **NO-GO for public launch or an external consumer pilot. HOLD all further GitHub writes until the product owner reviews this report.**

## Executive conclusion

RetirePilot has a reproducible **technical prototype**. The 71-file source import is on an unmerged draft PR. GitHub Actions succeeded on the PR head, and a fresh local test run passed 609 Python tests, 498 classifier checks and 13 API checks. Additional focused probes confirmed four bounded CPF reference behaviours and five priority-scenario safety restrictions. Those results do not constitute four independent assurance approvals.

The hard blockers are **full CPF and financial modelling**, **complete and safe high-value scenario integration**, **production-grade identity and security**, **independent financial and cybersecurity sign-offs**, **written Singapore legal scope advice**, and **48 real, consented consumer sessions**. The prior hypothetical consumer PASS remains a planning assumption, not an actual research result.

## Eight-step status and evidence

| Step | Status | Observed result | Required before passing |
|---|---|---|---|
| 1. Merge PR #10 | HOLD FOR REPORT | Draft, open, mergeable; 71 files; 0 PR reviews; GitHub CI success | Review exact diff and source; confirm approval; merge and rerun CI on main |
| 2. CPF and finance | PARTIAL / NO-GO | Bounded age-55 transfer for 2026/27, published CPF LIFE illustration lookups, terminal-month fix | Full account transitions, timing, interest and contributions; tax/housing consistency; independent golden cases |
| 3. Five scenarios | PARTIAL / NO-GO | S020, S030, S004, S016 return arithmetic previews only; S012 divorce blocked | Complete event semantics, household projection integration, approved controls and independent results |
| 4. Production security | FAIL / NO-GO | No authenticated evaluate endpoint; arbitrary RP-SYNTH-prefixed ID accepted; household sharing blocked | Real identity, separate adult consent, tenant isolation, key custody, rate controls and tested deployment |
| 5. Independent finance | NOT PASSED | 0 external signed financial approvals | Reviewer qualified and independent, accepted scope, reconciled calculations, signed report |
| 6. Independent security | NOT PASSED | 0 external signed security approvals or deployed pen test | Independent architecture/threat review and penetration test with resolved P0 findings |
| 7. Singapore legal | NOT CLEARED | Regulatory issue spotting, no retained legal opinion | Qualified advice on FAA boundary, PDPA and pilot conditions; resolve restrictions |
| 8. Real research and pilot decision | NOT STARTED / NO-GO | 48 recruitment slots; 0 real interviews, 0 approved researcher | 48 real sessions, de-identified evidence, comprehension/accessibility acceptance and signed pilot decision |

## Reproducible engineering evidence

- **GitHub:** open draft PR #10; head commit `24996da69269add2bf294fc5e598e8cd4597d9fd` based on `main`. GitHub Actions run `41750449875`, conclusion SUCCESS, included Python pytest, rule contracts and local API smoke checks. No recorded pull-request review.
- **Local verification:** `python -m pytest -q` 609/609 PASS; `PYTHONPATH=. python audit/run_rule_contracts_v22.py` 498/498 PASS; `PYTHONPATH=. python audit/run_api_checks.py` 13/13 PASS. Local source tree: `/mnt/data/rp_git_import_v27`.
- **Additional probes:** 17 checks executed with reproducible synthetic inputs. All 17 observations reproduced expected code behaviour. In particular, two probes succeeded at **demonstrating security weaknesses**, not passing the security gate.
- **Secret hygiene:** heuristic pattern scan of 71 text files did not match known private-key/token patterns. Not an exhaustive repository-wide scanner or external audit.
- **Original local handover ZIP SHA256:** `2746a152f267769f8653aa6fed987d3e6881547e8669d87de9bb0a24182eab98`. This ZIP is not a GitHub-reviewed release artifact.

## Financial and CPF findings

1. Official CPF sources indicate that the 2026/27 FRS for members turning 55 is S$220,400 and S$228,200 respectively. The reference function transfers SA savings followed by OA up to the cohort FRS, closes SA and conserves balances on the exact 55th birthday. The test reproduces these bounded examples. This is **not a monthly CPF projection**.
2. CPF LIFE source tables provide **illustrative male Standard Plan** 2026 figures. RetirePilot's exact 2026 S$220,400 reference gives S$1,780 monthly from age 65. The approved product decision remains member-supplied **official personal estimates**, not inferred payouts.
3. Full contribution allocation, monthly interest and extra interest, retirement account changes after 55, property refund/withdrawal interactions, self-employed and platform-worker regimes, and member-specific CPF LIFE plan choices remain insufficiently modelled and independently unvalidated.
4. The previously reproduced terminal partial-month income overstatement has a local regression fix. It is covered in the PR test suite, but independent finance review is still outstanding. Keep GitHub issue #9 open until a qualified reviewer verifies it.

Official references: https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum ; https://www.cpf.gov.sg/service/article/what-happens-to-my-cpf-savings-when-i-turn-55 ; https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month ; https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates

## Five priority scenarios

| Scenario | Current capability | What is missing |
|---|---|---|
| S020 Housing downsizing | Sale costs - mortgage - official member-reported CPF refund - replacement cash arithmetic | CPF refunds back to accounts, stamp duty, HDB eligibility and timing, actual housing cash flow |
| S030 CPF payout timing | Compare two member-transcribed official CPF LIFE monthly estimates | Full cash-flow timing, life horizon and survivorship interpretation |
| S004 Reduced working hours | Compare member-reported net cash salaries for bounded months | Recalculate actual CPF, tax, commissions and career transitions |
| S016 Parent care | Added cash caregiving expenses for bounded months | Leave, subsidies, reimbursements, medical/insurance variables |
| S012 Divorce/family transition | Explicitly blocked | Legal division, maintenance, property rights, verified consent and custody assumptions |

All five currently set `may_post_to_household_projection=false`. Their correct limited previews should not be called complete integrated scenarios. The broader 46-entry catalogue has 26 newer design contracts and 20 pre-existing bounded mappings. No claim of 46 production-ready events is justified.

## Security and data-protection findings

- A TestClient request to `/api/evaluate` with an arbitrary, fabricated `RP-SYNTH-...` ID and an unrecognised field returned HTTP 200. The prefix is an insufficient real-data guard. A second probe confirms no authentication is required to access this endpoint. These are **release-blocking** for any public/customer service.
- The local vault encrypts stored profile/action contents, tests consent withdrawal and refuses household sharing; that is a narrow research safeguard, not a secure hosted multi-user system.
- Additional requirements: authenticated users, independently verified consenting adults, per-person data scopes, tenant separation, key custody/rotation, TLS/infrastructure, audit policies, logging minimisation, secure deletion and independent penetration testing.

## Legal status and human participation

- MAS's published financial advisory guidance applies a two-stage test to activities that may amount to financial advice and carrying on a business. The 1A limitation to educational planning reduces intended scope, but an actual-feature regulatory analysis by a Singapore lawyer is still required.
- PDPC obligations apply to the use and disclosure of personal data. User consent, household-specific authority, protection, retention and transfer processes require professional assessment for the proposed real-data product.
- Four exploratory emails were previously sent seeking a financial reviewer, a security reviewer, Singapore legal advice and a 48-person research recruitment quote. A fresh linked Gmail search found **no replies** from the four organisations. No fee, appointment or assurance opinion is established.
- The planned 48 participants are **not actual participants**. The study cannot be waived by a product-owner assumption or by 48 synthetic workflows. No production data collection is authorised.

Official references: https://www.mas.gov.sg/regulation/guidelines/guidelines-on-provision-of-financial-advisory-service ; https://apps.pdpc.gov.sg/resources/pato/introduction ; https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic

## Readiness and next action sequence

1. **Pre-push hold:** Do not merge or modify GitHub. Give product owner this report. Request a specific approval to merge PR #10 only after the review is complete.
2. **Financial engineering:** Create independently specified CPF golden cases and year-by-year balance-ledger methodology; refuse unsupported paths; address five complete scenario models, especially housing/care, before widening scope.
3. **Security engineering:** Require a real identity and consent provider before any production data, add data-scope and tenant enforcement, produce a threat model and arrange independent testing.
4. **Assurance:** Evaluate independent reviewer qualifications, conflicts, proposals and quotes. User approval is required before spending. Capture signed and dated evidence on the reviewed commit.
5. **Consumer research:** Obtain approved recruitment supplier and consent protocol, complete 48 actual studies, correct critical comprehension and accessibility problems and retest.
6. **Pilot GO/NO-GO:** Gate only after all prior verified evidence and accountable sign-offs are complete. Otherwise remain **NO-GO**.

## Audit limitations and decision

This is an **internal engineering and evidence audit**, not a qualified financial opinion, security certification, legal opinion or participant study. It cannot compel replies, appoint paid professionals or manufacture real consumer feedback. No further GitHub push, merge, issue write or comment was performed during this assessment.

**FINAL PRE-PUSH DECISION: HOLD / NO-GO.** Existing draft source and successful CI are useful, but the requested condition of all eight steps successful **is not met**. Independent sign-offs and real consumer validation cannot be assumed or fabricated.
