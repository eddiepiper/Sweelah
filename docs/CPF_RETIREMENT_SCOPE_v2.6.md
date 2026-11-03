# CPF retirement reference module v2.6

**Scope: precise and deliberately restricted. No complete personal CPF retirement forecast.**

Implemented in the local v2.6 handover:
- A strict 55th-birthday **SA-first, OA-second** transfer into a new RA up to FRS for 2026 (SGD 220,400) and 2027 (SGD 228,200) cohorts, and SA closure/excess to OA. Valid only at the birthday snapshot with CPF membership confirmed, opening RA zero, no property pledge.
- An **exact six-row public CPF LIFE example table lookup** for male Standard Plan 2026 illustrations at start ages 65 and 70. It refuses interpolation, other plan types and personal payout estimates.
- A cash-only windfall operator for confirmed net receipts, not inheritance or tax advice.

**Not implemented:** full future CPF contributions and allocation, RA/SA transitions for other cohorts, CPF interest account transaction timing, future retirement income, actual CPF LIFE quotation, pension options or tax decisions. No authority to use for individual financial advice.

Sources:
- https://www.cpf.gov.sg/service/article/what-happens-to-my-cpf-savings-when-i-turn-55
- https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum
- https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month
- https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates

**Local test result:** 588/588, with source migration CI not yet confirmed. **Phase 9: NO-GO.**
