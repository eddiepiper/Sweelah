# RetirePilot v2.7: Approved Decisions and Bounded Remediation

**Product decisions approved 2026-11-04:** 1A, 2A, 3A, 4A, 5A, 6A, 7A. See `docs/APPROVED_DECISIONS_v2.7.json` and the PSD/TSD v2.7.

## What actually changed

- **P0 terminal-month forecast corrected:** fractions now use the full calendar month as denominator. S$7,200 Jan 1-May 20, 2027 now produces **S$33,212.90** (not S$36,000).
- **CPF LIFE provenance enforced:** personal payout streams require a member-transcribed official estimate. Synthetic fixtures may use the explicit synthetic estimate source. Published CPF tables remain illustrations only.
- **Uncalibrated numerical confidence hidden:** public `evaluate` response and consumer UI show possible persona descriptions only; internal 96-rule engine remains auditable.
- **Household sharing fail-closed:** local `LocalVault.share_household_records` always rejects any sharing because separate adult identity/consent authentication is not integrated. Synthetic consent is not genuine identity verification.
- **Five priority scenarios:** S020 downsizing, S030 member-supplied payout timing, S004 part-time income, S016 parent care and S012 divorce are explicitly defined. Four have limited financial previews, S012 is blocked. None are complete end-to-end life-event engines.
- **Release controls endpoint:** `GET /api/release-controls` reports unavailable identity/consent verification, blocked sharing and NO-GO.

## Verification evidence

- `python -m pytest -q`: **609 passed** (internal local self-run, synthetic data only)
- `PYTHONPATH=. python audit/run_rule_contracts_v22.py`: **498/498 passed**; tests internal rule consistency, not external classification accuracy
- `python audit/run_api_checks.py`: **13/13 passed** (the 13 existing smoke routes; new release-controls endpoint tested in pytest)
- No GitHub CI, independent professional approval, real-person authentication, or consumer interviews have been completed or implied by the above.

## Source and scope

This ZIP is an engineering handover, not evidence of a successfully migrated GitHub repository. The private GitHub decision register is separately committed. Before merging into `main`, import the exact code and tests through reviewed change control and run CI. Do not enable a public service or use customer financial records.

## How to run

```bash
python -m pip install -r requirements.txt
python -m pytest -q
PYTHONPATH=. python audit/run_rule_contracts_v22.py
python audit/run_api_checks.py
python -m uvicorn retirepilot.api:app --host 127.0.0.1 --port 8766
```

**External pilot: NO-GO.** Reviewers: inquiries only; no signed financial, security or Singapore legal opinion. Consumer testing: 0 of 48 observed sessions.
