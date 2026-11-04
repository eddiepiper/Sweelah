# Atlas Business-Logic Handover v1.8

**Approval date:** 4 November 2026  
**Decision authority:** RetirePilot product owner  
**Scope:** Financial and scenario design rules. This does not request production-security implementation or legal clearance.

## Source of truth

- [Approved decisions D08-D16](APPROVED_BUSINESS_RULE_DECISIONS_D08_D16.md) (nine approved defaults)
- [Machine-readable decision register](APPROVED_PRODUCT_DECISIONS_D08_D16.json)
- [18 financial engine contracts](financial_engine_contracts_18.json)
- [46 scenario contracts](scenario_engine_contracts_46.json)
- [48 synthetic consumer walkthroughs](synthetic_consumer_walkthroughs_48.json)
- [Consumer tabletop roleplays](48_ROLEPLAY_SESSION_SCRIPTS_synthetic.md)
- [Business Rulebook v1.8, approved defaults](RetirePilot_Business_Rulebook_v1.8_Approved.xlsx)

## Engineering delivery criteria for Atlas

1. Every engine identifies source facts, ownership, currency, effective dates, data provenance and missing-data handling; unknown must not silently become zero.
2. Dated CPF, IRAS, platform-worker and other financial rules must cite official reference tables and include golden numerical cases, exceptions and transition boundaries. Unpublished statutory rates are explicit user assumptions, not official future law (D08).
3. Reconcile take-home cash, CPF accounts OA/SA/MA/RA, accessible savings, debt and taxation without gross/net or asset-sale double counts.
4. CPF LIFE personal payouts are **member-provided official estimates**, never inferred from published examples or modelled as actuarial facts.
5. In a shortfall, use spendable cash above the user-defined reserve, then user-approved liquid assets. Do not infer borrowing, forced selling or restricted CPF access (D09).
6. Show alternative horizons at ages 90/95/100, not a single prediction (D10).
7. Housing downsizing requires documented sale proceeds waterfall, CPF refunds, replacement financing and dated settlement; otherwise display shortfall and no affordability verdict (D11).
8. Unverified subsidies, insurance or inheritance are conditional upside only, excluded from baseline (D12).
9. Overseas scenarios remain dated documented cashflow and FX simulations, not unverified foreign tax/eligibility claims (D13).
10. Consumer output shows cash runway, shortfall and assumptions, not invented readiness or persona-confidence scores (D14).
11. Without partner permission, use only confirmed individual-owned facts. Missing spouse data stays unknown (D15).
12. Compound scenarios use owner-specific dated state transitions and deterministic conflict detection; do not double count (D16).
13. Maintain a coverage matrix separating **specified**, **implemented**, **internally tested**, **independently verified**, and **blocked** for each F01-F18 and S001-S046.

## Evidence boundaries and open work

- **18 financial engines and 46 scenarios:** Business contracts defined; calculations and sources not all independently reconciled.
- **48 synthetic roleplays:** Tabletop design coverage only, **0/48 real consumer interviews**.
- **Security and legal:** Out of the present business-rule analysis scope, not waived for eventual external pilot.
- **Release:** NO-GO for Phase 9 until all required release gates pass.
- **Baseline:** Existing v2.7 code on main; any separate v2.8 code must be independently reviewed and committed on its own engineering PR.

**Approved for requirements handoff to Atlas, not certified as financial or consumer-tested.**
