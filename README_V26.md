# RetirePilot v2.6: CPF + Complete Scenario Design Mapping

**Synthetic research only. External pilot / personalised financial advice: NO-GO.**

From `RetirePilot_v2.5_Full_Source_Migration`, v2.6 adds:

- All 46 scenario IDs assigned explicit contracts; 26 former gaps are mapped, seven to opt-in limited financial converters and 19 blocked until dedicated modelling exists. The old 20 mappings remain bounded.
- An exact-date 55th-birthday CPF RA transfer snapshot for 2026/2027 cohorts, with SA-first and OA-second transfer and SA closure.
- Official 2026 male Standard Plan CPF LIFE **example table lookup only**, no guessed personal payout.
- An explicitly confirmed net-cash windfall operator and fail-closed scenario compiler.
- Updated review/recruitment register. Four external non-binding RFIs sent, with no commitments.

**Local verification:** `python -m pytest -q` => 588/588; classifier `audit/run_rule_contracts_v22.py` => 498/498; API `audit/run_api_checks.py` => 13/13. Self-run synthetic tests, not external verification.

See `docs_v26/ENGINEERING_AND_RELEASE_GATE_v26.md` and `docs_v26/EXTERNAL_ENGAGEMENT_AND_RECRUITMENT_v26.md`.
