# RetirePilot v2.5: Integrity Remediation and Independent Review Handoff

**Date:** 2026-11-04. **Classification:** local synthetic-only research prototype. **Phase 9: NO-GO.**

## This build actually changes

1. **Scenario target integrity:** `projection_v22.py` now rejects nonexistent and incompatible income IDs, unsupported housing shocks without a mortgage, rent shocks without a rent record, and scenarios whose whole duration has elapsed before the assessment year. A cash-only market portfolio legitimately shows zero stock-market loss rather than being rejected.
2. **Misleading task verification corrected:** `local_vault_v24.py` can no longer promote a self-described textual reviewer and evidence string into a genuinely `verified` action. Only `simulated_verified` is possible; it retains `verified_complete=False` and explicit `simulation_only=True` for the local demonstration. There is no authenticated verification provider.
3. **Published-table reference tests:** `tests/test_release_integrity_v25.py` adds 12 IRAS tax-table and seven CPF 2026/2027 amount anchors, plus scenario and synthetic-verification misuse tests. These are self-authored tests based on published tables, **not independent expert sign-off**.
4. **Independent review handoff:** `docs_v25/EXTERNAL_ASSURANCE_PACK.md` specifies the artifacts, reviewer separation, evidence demands and release gates. `docs_v25/CONSUMER_RESEARCH_EXECUTION_PACKAGE.md` sets out the evidence collection requirements for the still-unstarted 48-user study.
5. **Versioned findings:** v1.6 of the Excel Master Library adds new gates and official-table test anchors without changing the approved 18 dimensions or 96 archetype IDs.

## Run in a clean synthetic environment

```bash
python -m pip install -r requirements.txt
python -m pytest -q
PYTHONPATH=. python audit/run_rule_contracts_v22.py
python audit/run_api_checks.py
PYTHONPATH=. python audit/demo_vault_workflow_v24.py
python -m uvicorn retirepilot.api:app --host 127.0.0.1 --port 8766
```

All run scripts use local synthetic records. The vault demo generates an ephemeral key. Do not persist real financial records in the prototype. Do not bind the server to a public network interface.

## Still not completed

- The 96 archetypes use proposed, common weights; 0 independent human labels and 0 approved calibrations.
- Full CPF accumulation/RA transfers/interest and official CPF LIFE calculations are not implemented; 2026/2027 contribution/tax calculations are narrowly bounded reference modules, not a full engine.
- Of the 46 scenario catalogue entries, 20 are mapped to 12 operators; 26 are unmapped. Mapping is not proof of complete event semantics.
- Persistent identity, tenancy, authenticated action verification, production key management, security certification and PDPA/legal assessment are absent.
- Live generative AI, official service/account integrations, action execution, and actual reminders are not ready.
- Independent finance/security/legal review: 0 signed approvals. Consumer interviews: 0 of 48.

**Final verdict:** The v2.5 additions close two reproducible misleading-behaviour defects and extend reference tests. They do not clear the pilot gate. See `audit/PHASE_REAUDIT_v25.md`.
