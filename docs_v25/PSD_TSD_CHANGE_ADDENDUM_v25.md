# RetirePilot PSD / TSD Change Addendum v2.5

This addendum supersedes specific statements in the older PSD v2.0 and TSD v2.0. It is not a full re-authoring or formal approval of those specifications.

## Product-facing changes

1. The user remains a Singapore citizen or PR aged 45+, with the 18-dimension, 96-archetype reference library unchanged.
2. The displayed top-three personas are proposed matches only. The weights are not calibrated; do not show them as retirement readiness or calibrated probabilities.
3. A scenario targeted to an incompatible or unknown income stream must be rejected with a clear explanatory error. A cash-only household may legitimately show a zero change for an equity market shock.
4. The action lifecycle ends with `reported_complete` or a explicitly **synthetic** `simulated_verified` status. No actual financial action has been officially verified. The system may not show "verified complete" based on locally supplied reviewer strings.
5. No user may interpret an annual tax-bracket reference or 2026/27 CPF contribution rate sample as their final personal tax or CPF position.
6. The assistant remains a local, deterministic guide. Live generative AI, bank/CPF connections, official confirmation and any regulated recommendations are outside the approved build.

## Technical changes

- `retirepilot/projection_v22.py`: scenario validation now checks targeted income identifiers, type compatibility, required rent/mortgage records, and fully expired scenario windows before calculation.
- `retirepilot/local_vault_v24.py`: `TRANSITIONS` no longer allows untrusted `verified` in the synthetic vault. It allows `simulated_verified` only with `synthetic-*` evidence and a different mock verifier. The output retains `verified_complete=False` and `simulation_only=True`.
- `tests/test_release_integrity_v25.py`: published-rate test anchors (IRAS resident tax 12 cases and CPF 2026/27 full-rate OW 7 cases), invalid-target tests and action verification misuse tests.
- API route schemas remain unchanged in v2.5; data still must be synthetic and routes remain bound to localhost.

## Release and evidence status

- All 96 archetypes evaluated; no approved empirical persona weights.
- 12 implemented scenario operators, 20 of 46 catalogue entries mapped, 26 unmapped.
- Local synthetic tests passing is not independent finance, regulatory, privacy or usability certification.
- Actual consumer interviews: 0 of 48 planned.
- External pilot gate: **NO-GO**.

This addendum, the re-audit report, and v1.6 Excel gates should be read before any older completion summaries.
