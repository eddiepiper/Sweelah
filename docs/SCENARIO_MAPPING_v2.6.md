# Scenario catalogue contract mapping v2.6

**2026-11-04 | Synthetic-only research | Phase 9 NO-GO.**

This is a **design-to-engineering mapping**, not implementation of 26 complete life events. The source is the existing 46-entry master catalogue. Twenty existing mappings were already bounded; the other 26 now have explicit contracts. Seven have newly tested *limited financial subcomponent converters* and **19 fail closed** pending dedicated engines. No external review has occurred.

| ID | Event | Mapping | Limited converter | Required evidence |
|---|---|---|---|---|
| S005 | Delayed retirement | `RETIREMENT_GOAL_ONLY` | YES, partial | new_retirement_age |
| S006 | Return to work | `NOT_SAFE_TO_COMPILE` | NO | rehiring offer, income, CPF |
| S012 | Divorce | `NOT_SAFE_TO_COMPILE` | NO | asset settlement, ownership, consents |
| S013 | Widowhood | `NOT_SAFE_TO_COMPILE` | NO | survivor income, estate, insurance |
| S014 | New child/dependant | `RECURRING_COST_COMPONENT` | YES, partial | extra_monthly, start, duration |
| S015 | Adult child support | `RECURRING_COST_COMPONENT` | YES, partial | extra_monthly, start, duration |
| S019 | Property-value decline | `NOT_SAFE_TO_COMPILE` | NO | property ID, value, mortgage |
| S020 | Downsizing | `NOT_SAFE_TO_COMPILE` | NO | sale, CPF refund, replacement property |
| S022 | Lease monetisation | `NOT_SAFE_TO_COMPILE` | NO | HDB eligibility and official quote |
| S025 | Low real returns | `NOT_SAFE_TO_COMPILE` | NO | asset returns by year, inflation |
| S026 | Poor early withdrawal returns | `NOT_SAFE_TO_COMPILE` | NO | dated returns and withdrawals |
| S027 | Concentrated stock loss | `NOT_SAFE_TO_COMPILE` | NO | holding-specific portfolio detail |
| S029 | Earlier retirement | `RETIREMENT_GOAL_ONLY` | YES, partial | new_retirement_age |
| S030 | Payout deferral | `NOT_SAFE_TO_COMPILE` | NO | official CPF LIFE estimates at selected ages |
| S031 | Voluntary top-up | `NOT_SAFE_TO_COMPILE` | NO | source funds, CPF top-up limits |
| S032 | Pre-payout funding bridge | `NOT_SAFE_TO_COMPILE` | NO | dated income and cash drawdown |
| S033 | Contribution interruption | `NOT_SAFE_TO_COMPILE` | NO | affected CPF streams and timing |
| S035 | Disability-related cost shock | `RECURRING_COST_COMPONENT` | YES, partial | extra_monthly, duration |
| S038 | Retire overseas | `NOT_SAFE_TO_COMPILE` | NO | destination, tax, healthcare, FX |
| S039 | Exchange-rate movement | `NOT_SAFE_TO_COMPILE` | NO | currency balances and rate timeline |
| S040 | Repatriation | `NOT_SAFE_TO_COMPILE` | NO | residency, taxes, relocations |
| S041 | Foreign pension change | `NOT_SAFE_TO_COMPILE` | NO | foreign pension terms, FX, tax |
| S042 | Inheritance | `NET_CASH_RECEIPT_COMPONENT` | YES, partial | confirmed net cash received |
| S043 | Business sale | `NOT_SAFE_TO_COMPILE` | NO | net sale proceeds, liabilities, earnings |
| S044 | Major gift to children | `NET_CASH_GIFT_COMPONENT` | YES, partial | net cash gift amount |
| S046 | Business failure | `NOT_SAFE_TO_COMPILE` | NO | debts, guarantee exposures, income |

## Exact meanings

- `RETIREMENT_GOAL_ONLY`: adjust the primary retirement age only. No future CPF contributions, tax, LIFE or actuarial recalculation.
- `RECURRING_COST_COMPONENT`: user-supplied cash cost only, not a complete health/family event.
- `NET_CASH_RECEIPT_COMPONENT`: confirmed net cash inflow; no inheritance entitlement, probate or tax prediction.
- `NET_CASH_GIFT_COMPONENT`: reported cash gift outflow only.
- `NOT_SAFE_TO_COMPILE`: deterministic refusal. Never translate a complex event to a generic percentage without verified financial semantics.

## Tests and release boundary

The v2.6 package was locally tested: **588/588 Python**, **498/498 classifier contract**, **13/13 API**. These are self-run synthetic tests, *not* GitHub CI or independent assurance. Source import to this repository is still tracked in Issue #1.
