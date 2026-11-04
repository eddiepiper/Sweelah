# v2.6 Scenario contract mapping: formerly unmapped 26

Scope: 26 prior gaps now have explicit contracts. Seven support a **limited financial component**, not complete event semantics. Nineteen remain **blocked** pending dedicated modelling.

| ID | Event | Strategy | Implemented limited component? | Required inputs |
|---|---|---|---|---|
| S005 | Delayed retirement | RETIREMENT_GOAL_ONLY | YES | new_retirement_age |
| S006 | Return to work | NOT_SAFE_TO_COMPILE | NO | rehiring_offer, effective_date, income, employer CPF |
| S012 | Divorce | NOT_SAFE_TO_COMPILE | NO | asset_ownership, consent, legal_settlement, housing, dependants |
| S013 | Widowhood | NOT_SAFE_TO_COMPILE | NO | survivor_income, insurance, estate, household_consents |
| S014 | New child/dependant | RECURRING_COST_COMPONENT | YES | extra_monthly, start_year, duration_years |
| S015 | Adult child support | RECURRING_COST_COMPONENT | YES | extra_monthly, start_year, duration_years |
| S019 | Property-value decline | NOT_SAFE_TO_COMPILE | NO | specific_property_id, valuation, ownership, mortgage |
| S020 | Downsizing | NOT_SAFE_TO_COMPILE | NO | sale_price, CPF_refund, replacement_home, stamp_duty, moving_cost |
| S022 | Lease monetisation | NOT_SAFE_TO_COMPILE | NO | HDB_eligibility, lease_age, official_quote, CPF_refund |
| S025 | Low real returns | NOT_SAFE_TO_COMPILE | NO | return_path_by_asset, inflation_path, market_timing |
| S026 | Poor early withdrawal returns | NOT_SAFE_TO_COMPILE | NO | withdrawal_timing, asset_class_returns, return_sequence |
| S027 | Concentrated stock loss | NOT_SAFE_TO_COMPILE | NO | holding_id, holding_value, loss_rate, portfolio_allocation |
| S029 | Earlier retirement | RETIREMENT_GOAL_ONLY | YES | new_retirement_age |
| S030 | Payout deferral | NOT_SAFE_TO_COMPILE | NO | official_CPF_LIFE_estimate_65_70, start_age |
| S031 | Voluntary top-up | NOT_SAFE_TO_COMPILE | NO | source_account, RA_topup_allowance, verified_cash_availability |
| S032 | Pre-payout funding bridge | NOT_SAFE_TO_COMPILE | NO | cash_bridge_horizon, essential_expenses, official_payout_start |
| S033 | Contribution interruption | NOT_SAFE_TO_COMPILE | NO | affected_CPF_income, contribution_months, residency_cohort |
| S035 | Disability-related cost shock | RECURRING_COST_COMPONENT | YES | extra_monthly, start_year, duration_years |
| S038 | Retire overseas | NOT_SAFE_TO_COMPILE | NO | jurisdiction, residence_status, expenses, taxes, FX, healthcare |
| S039 | Exchange-rate movement | NOT_SAFE_TO_COMPILE | NO | currency, FX_path, foreign_assets, liabilities |
| S040 | Repatriation | NOT_SAFE_TO_COMPILE | NO | residence_history, relocation_costs, tax_domicile, FX |
| S041 | Foreign pension change | NOT_SAFE_TO_COMPILE | NO | foreign_pension_currency, indexation, source, taxes |
| S042 | Inheritance | NET_CASH_RECEIPT_COMPONENT | YES | net_received_once, start_year |
| S043 | Business sale | NOT_SAFE_TO_COMPILE | NO | sale_net, liabilities, owner_shares, future_business_income |
| S044 | Major gift to children | NET_CASH_GIFT_COMPONENT | YES | net_cash_gift_once, start_year |
| S046 | Business failure | NOT_SAFE_TO_COMPILE | NO | business_debt, liability_guarantees, income_history, personal_exposure |

## Definitions

- `RETIREMENT_GOAL_ONLY`: alter primary retirement age; no CPF, tax or employer contribution recalculation.
- `RECURRING_COST_COMPONENT`: add user-supplied recurring care/support costs only.
- `NET_CASH_RECEIPT_COMPONENT`: confirmed NET cash inflow only, no legal entitlement or tax estimate.
- `NET_CASH_GIFT_COMPONENT`: confirmed cash gift outflow only.
- `NOT_SAFE_TO_COMPILE`: explicit refusal until case-specific full engine exists.

## Evidence

- Local v2.6 synthetic suite: 588/588.
- Legacy 96-persona contract checks: 498/498.
- Local API smoke: 13/13.
- Entire 46-row registry resides in the versioned package; 20 pre-existing scenario mappings were unchanged.
- Full source migration to GitHub is a separate open issue; **these statuses are not a GitHub CI result.**

**Phase 9: NO-GO.**
