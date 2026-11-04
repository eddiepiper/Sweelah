# RetirePilot v2.7: Engineering Remediation Record

> **Source-control update (2026-11-04):** The migration originally marked as pending below was completed on the v2.7 review branch in PR #10. Original PSD/TSD Word and PDF files, Master Library v1.7, validation evidence and a checksum verifier were added. GitHub CI passed on the combined source and documentation commit. The historical audit text below remains as originally reported. **Phase 9 is still NO-GO.**


**Approved decision set:** 1A, 2A, 3A, 4A, 5A, 6A, 7A (2026-11-04)  
**Primary decision register:** [APPROVED_DECISIONS_v2.7.md](APPROVED_DECISIONS_v2.7.md)  
**Source of implementation evidence:** locally packaged v2.7 derivative of v2.6, not GitHub main.  
**Phase 9:** NO-GO.

## Verified locally (fresh extracted v2.7 package)

| Check | Outcome | Evidence boundary |
|---|---:|---|
| Python unit/integration/decision tests | **609/609 PASS** | Self-run synthetic, not GitHub CI |
| Persona rule contracts | **498/498 PASS** | Internal rule consistency, not calibration |
| Existing API smoke checks | **13/13 PASS** | Existing API routes; new read-only controls covered in pytest |
| Code ZIP integrity | PASS | No corrupted archive member |
| Consumer study | **0/48 real sessions** | Hypothetical acceptance only for planning |
| External financial/security/legal opinion | **0 signed approvals** | No qualifications/quotes accepted |

## P0 projection defect corrected locally, Issue #9 remains open

An end-of-horizon birthday used to reduce the denominator of monthly income/expense fractions, effectively treating a partial final month as a full one. Correct formula uses the **full calendar month's day count**.

Synthetic reference: annual 2027 earned cash income of S$7,200 per month, from 1 Jan to 20 May exclusive: 4 full months plus 19/31 of May = **S$33,212.90**, down from the old **S$36,000**. Independent tests cover the 1st-of-month birthday and expense proration. **Issue #9 cannot be closed until this fix is committed to source control, passes GitHub CI and is independently reviewed.**

## Product-decision changes

- **1A Educational only:** Keep product-specific financial recommendations and automatic financial transactions blocked.
- **2A CPF LIFE:** A personal payout income record must declare a member-transcribed official estimate. A public CPF illustration is not a personal income estimate. Source is user-asserted, NOT independently authenticated.
- **3A 96 provisional personas:** Retain internal scoring for QA; redact numeric confidence, thresholds and raw scores from public assessment/API and visible UI.
- **4A Household consent:** New share method ALWAYS refuses sharing. Real person-specific authentication/consent provider is NOT built. Local synthetic consent cannot be described as identity verification.
- **5A Priority scenarios:** S020 downsizing, S030 payout timing, S004 part-time employment, S016 parent care, S012 divorce. Four limited arithmetic previews; S012 blocked pending legal and consent review. None is complete.
- **6A Reviewer engagement:** Qualifications, independence, scopes and quotations first; no paid appointments or approvals.
- **7A Research:** Hypothetical consumer PASS is a development-planning assumption only. 48 actual interview/usability sessions remain required.

## Source-level change inventory (local, not in GitHub)

- retirepilot/projection_v22.py
- retirepilot/core.py
- retirepilot/service.py
- retirepilot/assistant.py
- retirepilot/api.py
- retirepilot/ui.html
- retirepilot/local_vault_v24.py
- retirepilot/priority_scenarios_v27.py (new)
- tests/test_approved_decisions_v27.py (new)
- docs/APPROVED_DECISIONS_v2.7.json (new)
- README_V27.md (new)
- docs_release/RetirePilot_PSD_v2.7.docx and .pdf
- docs_release/RetirePilot_TSD_v2.7.docx and .pdf

The exported v2.7 ZIP contains 77 files and SHA256:
e4fd906bd0ffa987b6370ab55c5135114cefa48aad46e21adc3803905e4a4a49

## External dependency gates

Financial SME numerical reconciliation, production security architecture and test, Singapore-qualified written legal opinion, 96-persona calibration, and 48 real user sessions remain OPEN. A source-based legal review and code self-test cannot substitute for these approvals.

## GitHub source-control caveat

The GitHub repository still contains project decisions and audit evidence, **not the complete migrated Python application**. No GitHub Actions pipeline has been run against v2.7. Keep source migration #1 and the P0 projection issue #9 open. Do not publish a production service or accept real customer data.
