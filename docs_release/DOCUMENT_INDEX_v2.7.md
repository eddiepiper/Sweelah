# RetirePilot v2.7: Document delivery index

**Approved product decisions:** 1A–7A, 4 November 2026.  
**Technical baseline:** v2.7 review branch.  
**External pilot:** **NO-GO**. This is documentation and source-control housekeeping only, not regulatory or professional approval.

This directory contains the original, byte-for-byte v2.7 product and technical specifications, the v1.7 rulebook, and the internal validation reports. SHA-256 checksums and file sizes are recorded in `BINARY_DOCUMENT_MANIFEST_v2.7.json`.

| Document | Purpose |
|---|---|
| [RetirePilot_PSD_v2.7.docx](RetirePilot_PSD_v2.7.docx) | Product Specification v2.7 (editable) |
| [RetirePilot_PSD_v2.7.pdf](RetirePilot_PSD_v2.7.pdf) | Product Specification v2.7 (PDF) |
| [RetirePilot_TSD_v2.7.docx](RetirePilot_TSD_v2.7.docx) | Technical Specification v2.7 (editable) |
| [RetirePilot_TSD_v2.7.pdf](RetirePilot_TSD_v2.7.pdf) | Technical Specification v2.7 (PDF) |
| [RetirePilot_Master_Library_v1.7.xlsx](RetirePilot_Master_Library_v1.7.xlsx) | Master Rulebook v1.7 with scenario/research worksheets |
| [RetirePilot_PrePush_Gate_Report_2026-11-04.pdf](RetirePilot_PrePush_Gate_Report_2026-11-04.pdf) | Internal pre-push gate report (PDF) |
| [RetirePilot_PrePush_Gate_Report_2026-11-04.md](RetirePilot_PrePush_Gate_Report_2026-11-04.md) | Internal pre-push gate report (Markdown) |
| [RetirePilot_PrePush_Evidence_2026-11-04.zip](RetirePilot_PrePush_Evidence_2026-11-04.zip) | Reproducible internal test evidence |
| [RetirePilot_Validation_Audit_2026-11-04.pdf](RetirePilot_Validation_Audit_2026-11-04.pdf) | Earlier internal financial/security/legal audit |

## Verification

Run from the repository root:

```bash
python scripts/verify_release_documents.py
```

This verifies SHA-256 and size for every binary and text deliverable, PDF/OOXML/ZIP file integrity, and the presence of key proof phrases. GitHub CI includes this check on pull requests and on `main` after merging.

## Gate boundaries

- CI and binary integrity checks do **not** validate financial rule accuracy or authorise a pilot.
- Financial: partial CPF/account simulations, independent reconciliation still required.
- Security: API authentication and separately verified adult identity/consent are missing.
- Legal: no independent written Singapore-qualified regulatory opinion.
- Consumer: **0/48** real interviews; synthetic workflows are not consumer validation.
- Five priority scenarios remain limited previews, not complete certified engines.
- Current release status: **Phase 9 NO-GO**.

A passing documentation CI check means these files are committed and unchanged. It does not imply the product is ready for real customer data.
