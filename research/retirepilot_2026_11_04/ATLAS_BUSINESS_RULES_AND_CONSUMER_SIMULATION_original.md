# RetirePilot: Business Logic and 48-Consumer Synthetic Simulation
**Date:** 4 November 2026  |  **Scope:** financial and scenario business logic only  |  **Code changes:** none  |  **GitHub changes:** none

## Evidence boundaries

- This is a **constructed tabletop evaluation**: 48 distinct synthetic Singapore citizen/PR household situations. No real human subjects were interviewed, no consent was taken, and no observed usability measurements exist. Real consumer research remains **0/48**.
- This document describes required engine behaviour **before Atlas builds**; it does not represent implemented or independently validated financial calculations.
- The original v2.8 catalogue has 46 scenarios, most with limited or unsupported implementation. Here **46/46 receive business-rule contracts**, not implementation sign-offs.
- Security architecture and legal clearance were excluded from this review at the user’s request. Where they affect truth (divorce, inheritance, ownership), the contract uses only documented facts or safely refuses to calculate.

## Synthetic walkthrough results

| Metric | Count | Meaning |
|---|---:|---|
| Distinct scripted consumer cases | 48 | eight groups, six cases per group |
| Scenario catalogue IDs exercised | 46/46 | two deliberately repeated edge scenarios |
| Design-specified responses | 28 | calculable if required facts provided, not observed UX success |
| Conditional factual responses | 16 | only confirmed inputs may be included |
| Protective blocks | 4 | no fabricated entitlement or ownership |
| Actual observed participant sessions | 0/48 | no human fieldwork |

**Simulation design verdict:** all 48 scripted cases have a defined expected product response, including protective refusal. **Consumer validation is not passed.**

## 18 financial-engine requirements

| Engine | Description | Required inputs | Calculation or decision contract | Open status |
|---|---|---|---|---|
| F01 | Household fact and provenance register | Per adult date of birth, SC/PR/status dates, owner of every asset/liability, dependants, consent for specific data, evidence date | Immutable dated fact inputs and ownership; unknown ≠ zero; never impute spouse CPF | Core business rule specified; data provenance unresolved |
| F02 | Income stream and net household cash flow | Each stream type, gross/receipts, refunds, business costs, CPF/tax treatment, volatility, effective dates | Monthly attributable cash flows; gross != net; prevent double-counting between platform/SEP/salary; net available cash is after actual deductions | Build contract clear; complex stream verification needed |
| F03 | Employee CPF contributions and allocation | Age at payroll contribution, SC/PR entry year, employer count, OW/AW, eligible wage, year-specific tables, account caps | Apply published rate, wage ceilings, graduated PR bands, OW/AW cap and month-specific allocation. No 2028+ rate presented as known | 2026/27 bounded rules; future policy needs scenario assumption |
| F04 | Self-employed CPF / MediSave obligations | IRAS assessed net trade income by work year, age, CPF membership, business expense and platform exclusions | SEP MediSave due according to verified work-year table, not employee CPF rate; avoid duplicate platform earnings | Rule sources found; detailed table required |
| F05 | Platform-worker CPF | Operator report, net platform earnings, DOB, opt-in state, work year, earnings tier, contributions | Use platform rates for that year/opt-in cohort; avoid employee/SEP double count; report uncertain opt-in rather than guess | Official schedule identified; individual opt-in proof required |
| F06 | CPF OA/SA/MA/RA ledger and milestones | Opening dated account balances, transactions, interest rates by period, age, CPF withdrawal/transfer eligibility, BHS, FRS/ERS, property refunds | Ledger conservation per period; SA closure on 55th birthday; RA top-ups; BHS overflow according to applicable rules; interest accrues monthly, credited annually | Core end-to-end contract defined, full lifetime policies remain to verify |
| F07 | CPF LIFE cash-flow input | Member-reported official payout estimate by plan/start age/as-of date, supported eligibility facts | Treat official member-provided estimate as input, not generated yield; start only on selected date; show missing estimate as unknown, not zero | Approved decision 2A; no personal simulation formula |
| F08 | Housing and debt service | Property owner, valuation, financing currency, balance/rate/tenor, amortization, sale fees, official CPF property refund, stamp duty/lease constraints | Compute interest/amortization and equity separately; sale proceeds to loan then CPF refund, cash net; distinguish cash from CPF recredit; bridge funding only with explicit facilities | Event rules described; eligibility and exact waterfall must be externally checked |
| F09 | Tax and work-year reconciliation | Tax residency, income by category/year, allowable expenses/reliefs from evidence, YA, self-employed NI | Compute resident tax by confirmed YA schedule; assess reliefs only if documented; separate tax cash payment timing from tax liability | IRAS bands identified; complete relief catalogue pending |
| F10 | Investments and sequence risk | Asset holdings by currency and liquidity, costs, net income, return/inflation/FX paths, rebalancing assumptions | Value monthly and apply market returns before/after withdrawals consistently; no guaranteed return or invented recovery | Business model clear; scenario parameters/validation pending |
| F11 | Insurance and healthcare funding | Premiums, deductibles, confirmed coverage terms, claims approved, MediSave/Medishield/others, medical costs | Record costs immediately; model reimbursements only on confirmed amounts/eligibility; no promised payouts or double paid expenses | Require benefit/coverage facts, no presumed eligibility |
| F12 | Dependants, disability and caregiving | Per dependant costs and duration, caregiver employment effects, other family contributions, subsidies confirmed | Time-based cost schedules and separate income impacts; avoid creating subsidies or spouse resources without proof | Scenario rule clear for cash costs; support eligibility conditional |
| F13 | Other income and non-CPF retirement sources | Tenancy income/expenses, pension quote, annuity, commissions, sale proceeds, dividends, business revenues | Record source, owner, start/end, gross/net treatment and net effective cash only once | Build contract clear; individual terms require proof |
| F14 | Liquidity, decumulation and retirement gap | Retirement ages, horizon 90/95/100, essential/discretionary costs, reserve target, funding source order | Compute monthly funding gap before sales; preserve emergency reserve; restrict CPF; explicit ordered liquid withdrawals, no hidden debt financing | Source-specific waterfall needs owner decision |
| F15 | FX and cross-border cash flows | Source/destination country, currency, pension/gross net, FX monthly path, tax residence, conversion charges | Convert and date each exposure; do not guess jurisdiction-specific tax/pension rights or eligibility | Conditional until jurisdiction inputs sourced |
| F16 | Projection and explanation layer | Date-stamped facts, scenario parameter version, nominal/real price base, uncertainty ranges, policy-source version | Rebuild projections on each scenario and show before/after, marginal cash flow, CPF excluded from spendable cash, no single readiness-certainty score | Core contract ready; numeric calibration and comprehension remain unverified |
| F17 | Government benefits and retirement schemes | Scheme ID, eligibility evidence, effective-dated amount, actual application/award status | Show potentially relevant scheme only; separate indicative eligibility from confirmed award, do not add cash benefit until awarded | Research catalogue incomplete, no entitlement determination |
| F18 | Legacy and business transactions | Ownership, net realised amount, guarantees, liability, executor/settlement/official evidence, distribution date | Only confirmed net receipts and documented cash obligations enter forecast; no inheritance, divorce split or legal right guess | Bespoke facts mandatory; legal-driven entitlement intentionally not derived |

## 46 scenario contracts

| ID | Scenario | Financial dependencies | Business-rule effect | Safe refusal / guardrail |
|---|---|---|---|---|
| S001 | Retrenchment | F02,F03,F09,F14 | End affected salary on verified date, keep other streams, stop linked contributions; add severance only when confirmed | No default retrenchment benefit, CPF/pension income not invented |
| S002 | Pay reduction | F02,F03,F09 | Apply updated effective-date income; recalc employee CPF and tax from gross amount | Do not subtract gross cut as though it were net spending cash |
| S003 | Contract non-renewal | F02,F03,F14 | End fixed-term wage and contributions on stated contract end; bridge with documented available liquidity | Do not presume renewal or severance |
| S004 | Reduced working hours | F02,F03,F09,F14 | Replace current earned income and working hours for dated period; recompute linked CPF/tax and bridge | Current v2.8 preview only net earned-cash sensitivity |
| S005 | Delayed retirement | F02,F03,F06,F14 | Shift planned stop-work age later; extend wages/CPF accrual by employment type | No guarantee of employment continuation |
| S006 | Return to work | F02,F03,F04,F05,F07 | Insert dated new job stream and correct contribution scheme; leave CPF LIFE payments untouched absent official change | Do not assume rehiring, salary or pension suspension |
| S007 | Commission -50% | F02,F04,F09,F14 | Apply commission drop only to affected commission stream and re-evaluate costs, tax and SEP MediSave | Never haircut all household income |
| S008 | Platform suspension | F02,F05,F14 | Zero dated platform net earnings for affected operator; recompute platform CPF contributions | Other platform/non-platform streams continue |
| S009 | Declining orders | F02,F05,F14 | Recalculate net orders * net per order after fees; capture date range | Volume shock is not equivalent to gross revenue shock |
| S010 | Vehicle operating-cost shock | F02,F04,F05,F09 | Change dated vehicle operating expenses in correct stream; recalc net cash and relevant assessed income | Ensure no second deduction under household expenses |
| S011 | Loss of major client | F02,F09,F14 | Stop or reduce identified client stream with contractual notice/replacement assumptions | Do not apply portfolio-wide income haircut |
| S012 | Divorce | F01,F02,F08,F12,F18 | Model separate households after documented separation dates and agreed financial obligations only | Block property division, maintenance, CPF or custody assumptions without actual terms |
| S013 | Widowhood | F01,F02,F07,F11,F18 | On verified death event stop deceased income; introduce only confirmed survivors benefits, claims and estate receipts | Do not assume inheritance/insurance payouts, spouse CPF rights |
| S014 | New child/dependant | F02,F12,F17 | Introduce dated newborn/dependant recurring and one-time costs, medical and education | Benefits and grants conditional until confirmed |
| S015 | Adult child support | F02,F12,F14 | Add timed adult-child support; distinguish loan vs grant and one-time vs recurring | Avoid implied permanent support or double counting |
| S016 | Parent care | F02,F11,F12,F17 | Add parent care cost, time off and separate wage impact; reflect verified subsidies/insurance only | No automatic CareShield or MediSave reimbursement assumption |
| S017 | Loss of second income | F02,F03,F04,F05,F14 | Remove second adult stream on dated trigger and linked CPF/tax while preserving other adult data boundaries | Do not delete assets or assume spouse resources inaccessible |
| S018 | Mortgage repricing | F08,F02,F14 | Amortize existing housing loan with new rate from reset date and actual remaining term | Repricing does not refinance automatically |
| S019 | Property-value decline | F08,F14,F16 | Update property fair value and secured-equity estimate, leave cash and loan principal unchanged | Loss of net worth is not immediate cash outflow |
| S020 | Downsizing | F08,F06,F02,F14 | Sale proceeds less settlement/fees/CPF refund; separate OA/RA credits; replacement purchase, duties, bridge, new loan flows | CPF refunds are not available cash; eligibility and timing must be confirmed |
| S021 | Rent increase | F02,F12,F14 | Dated rent reset changes cash expense; apply deposits and moving fees only when provided | Avoid retroactive rent changes |
| S022 | Lease monetisation | F08,F06,F07,F14 | Use official scheme eligibility and quote, including lease, RA and proceeds, then model dated receipts | No estimated HDB Lease Buyback entitlement |
| S023 | Rental vacancy | F02,F08,F13 | Zero rent only in vacancy months but keep mortgage/tax/maintenance and vacancy expenses | Rental loss not property valuation loss |
| S024 | Equity market decline | F10,F14,F16 | Apply dated drawdown by asset class with liquidity conditions; continue portfolio path without assumed recovery | No guaranteed bounce-back |
| S025 | Low real returns | F10,F14,F16 | Apply real-return sensitivity to explicit nominal return and inflation paths per asset | Do not subtract inflation twice |
| S026 | Poor early withdrawal returns | F10,F14,F16 | Apply ordered path of early losses and withdrawals; recompute end capital and reserve | Sequence of returns matters, not just average return |
| S027 | Concentrated stock loss | F10,F14,F16 | Apply shock to named concentrated holding and denominator of total portfolio | Not a shock to entire investments |
| S028 | Inflation shock | F02,F10,F12,F16 | Apply category-specific expense and income indexing assumptions by dates | Do not equate inflation to investment loss |
| S029 | Earlier retirement | F02,F03,F06,F07,F14 | Move wage stop date earlier; recompute contributions and explicit liquidity bridge to official payout age | CPF LIFE start not moved earlier by early employment exit |
| S030 | Payout deferral | F07,F14,F16 | Compare separate member-provided official payout scenarios from 65/70 and bridging cash needs | No automatic best-age advice or generic uplift as personal quote |
| S031 | Voluntary top-up | F06,F07,F14 | Reallocate confirmed available cash/OA to RA under verified limits; revise payout only with new official member estimate | Do not award assumed tax relief or payout increase |
| S032 | Pre-payout funding bridge | F07,F14 | Calculate dated cash bridge until actual member-provided payout start; report reserve exhaustion | Cannot withdraw restricted CPF to plug deficit |
| S033 | Contribution interruption | F02,F03,F04,F05,F06 | Suspend contributor-specific CPF postings for verified months; recompute full cash/payroll interactions | Never assume CPF contributions continue after income stops |
| S034 | Medical expense shock | F11,F14 | Schedule immediate/recurring out-of-pocket cost and only verified reimbursements | Never assume insurance coverage pays |
| S035 | Disability-related cost shock | F02,F11,F12,F14 | Separate disabled-person spending, reduced wages and confirmed benefits into distinct dated streams | Do not infer disability-benefit eligibility |
| S036 | Long-term care expense | F11,F12,F14,F17 | Use staged care intensity, care period, out-of-pocket burden and documented payout policy | Do not presume policy eligibility or care duration |
| S037 | Caregiver income loss | F02,F03,F12,F14 | Stop/reduce caregiver earned income for documented leave; add support cost separately | No automatic statutory leave compensation |
| S038 | Retire overseas | F09,F13,F14,F15 | Combine location-specific cost, FX, foreign pensions, residency/tax status and healthcare | Block jurisdiction-specific unsupported rules |
| S039 | Exchange-rate movement | F10,F13,F14,F15 | Revalue each foreign-currency asset, liability and recurring receipt using dated FX path | Do not treat unrealised FX change as cash realised |
| S040 | Repatriation | F09,F13,F14,F15 | End offshore and start onshore incomes/costs with relocation expenses and tax residency changes | Residency rights and tax effects must be documented |
| S041 | Foreign pension change | F09,F13,F15 | Enter verified foreign pension gross/net and indexation rules with FX and withholding | No unverified foreign pension entitlement |
| S042 | Inheritance | F13,F14,F18 | Post confirmed net inheritance receipt after probate, costs and actual ownership transfer | Pending estate is not available cash |
| S043 | Business sale | F02,F09,F13,F14,F18 | Book verified sale proceeds after debt/fees and stop business earnings/equity upon closing | Avoid double-counting business value and sale proceeds |
| S044 | Major gift to children | F14,F18 | Reduce spendable liquid assets on dated cash gift, reflect other household only when ownership known | Do not gift restricted CPF balances |
| S045 | Estate expense | F11,F14,F18 | Book documented estate/probate expenses against correct paying estate/member | Do not charge a living member for hypothetical estate costs |
| S046 | Business failure | F02,F09,F13,F14,F18 | Cease business revenue, write down business equity, include documented personal guarantees/liabilities | Do not automatically transfer company debt to individual |

## 48 distinct simulated consumer challenges

| Case | Segment, age, language | Scenario | Synthetic consumer challenge | Expected response | Design state |
|---|---|---|---|---|---|
| SIM-001 | Salaried households, 45, English | S001 | My company is letting me go. Can you tell me how long my cash will last before CPF starts? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-002 | Salaried households, 48, Mandarin | S002 | My company cut my salary by a quarter. Is the impact on take-home cash the same? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-003 | Salaried households, 51, English | S003 | My contract ends in March. Do I keep CPF and income in your forecast after that? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-004 | Salaried households, 56, Malay | S004 | I want to work three days a week. What changes besides the monthly pay? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-005 | Salaried households, 60, English | S005 | If I work until 68 instead of 63, do you assume the company keeps me? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-006 | Salaried households, 64, Tamil | S006 | I am taking another job in retirement. Does this stop my CPF LIFE? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-007 | Platform and gig workers, 45, English | S007 | My commissions fell by half, but my base salary did not. Which figure changes? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-008 | Platform and gig workers, 49, Malay | S008 | My ride-hail account is suspended. Does the app still count my other delivery work? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-009 | Platform and gig workers, 51, Mandarin | S009 | I get fewer orders, but the platform fees vary. Are you using gross or net? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-010 | Platform and gig workers, 55, Tamil | S010 | Petrol and vehicle repairs have jumped. You are not subtracting them twice, right? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-011 | Platform and gig workers, 61, English | S011 | One client provides most of my income. If they leave, what other income remains? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-012 | Platform and gig workers, 68, Malay | S033 | I took six months off work. Does the CPF forecast still give me salary contributions? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-013 | Self-employed / property agents, 47, Mandarin | S018 | My mortgage goes from 2.6% to 4%. Will you keep the same loan term? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-014 | Self-employed / property agents, 50, English | S019 | My HDB value drops. Does your chart think cash left my bank account? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-015 | Self-employed / property agents, 54, English | S020 | I plan to sell the flat and buy smaller. How much cash do I actually have after CPF refund? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-016 | Self-employed / property agents, 58, Malay | S021 | My landlord raised rent in July. Does the higher amount begin only then? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-017 | Self-employed / property agents, 62, Mandarin | S022 | If I join the Lease Buyback Scheme, can you calculate benefits without an HDB quote? | Block numerical inference; explain missing proof and offer general educational alternatives | PROTECTIVE_BLOCK |
| SIM-018 | Self-employed / property agents, 67, English | S023 | My investment property is empty three months. Do mortgage costs continue? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-019 | Pre-retirees, 55, English | S024 | Markets crash 20%. Do you assume it all comes back next year? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-020 | Pre-retirees, 57, Mandarin | S025 | I am worried about inflation. Are these real returns or nominal returns? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-021 | Pre-retirees, 59, Malay | S026 | What if the market crashes early while I am drawing retirement income? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-022 | Pre-retirees, 61, English | S027 | My single stock position falls 70%. Why is the whole portfolio down 70%? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-023 | Pre-retirees, 63, Tamil | S028 | Healthcare inflation could outpace general inflation. Can I set that separately? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-024 | Pre-retirees, 64, English | S029 | I stop work at 60. Why does CPF LIFE not start until later? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-025 | Retirees, 65, English | S030 | CPF shows different estimates if I start at 65 or 70. Can I compare both and the cash gap? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-026 | Retirees, 66, Mandarin | S031 | If I top up RA, how do you know my actual payout will increase? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-027 | Retirees, 69, English | S032 | I plan to wait until age 70 for CPF payout. How do I pay my bills first? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-028 | Retirees, 71, Malay | S034 | I may need a medical procedure. Do you count my insurance reimbursement automatically? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-029 | Retirees, 74, English | S035 | Disability costs may rise and I may earn less. Are those separate assumptions? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-030 | Retirees, 78, Tamil | S036 | Care may get more expensive over time. Can you avoid assuming subsidies? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-031 | Family and caregivers, 46, English | S012 | We are separating. Please do not assume half the flat or my spouse CPF belongs to me. | Block numerical inference; explain missing proof and offer general educational alternatives | PROTECTIVE_BLOCK |
| SIM-032 | Family and caregivers, 50, Tamil | S013 | My partner died. Will you automatically assume I get all their CPF and insurance? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-033 | Family and caregivers, 54, Mandarin | S014 | Our family is adding a dependent. Will childcare grants already be counted? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-034 | Family and caregivers, 58, English | S015 | I support an adult child for two years. Can I set a definite end date? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-035 | Family and caregivers, 62, Malay | S016 | My mother needs help. Will you count her CareShield LIFE payout without proof? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-036 | Family and caregivers, 71, Mandarin | S017 | My spouse will stop working. Does that affect only one person’s income and CPF? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-037 | Lower-income / hardship, 45, Malay | S037 | I might leave work to care for family. Does the plan assume the government pays my salary? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-038 | Lower-income / hardship, 51, English | S042 | My parent’s estate is unresolved. Can I leave the inheritance out until it arrives? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-039 | Lower-income / hardship, 56, Mandarin | S044 | I want to give my daughter cash, but it must come from accessible savings. | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-040 | Lower-income / hardship, 60, Tamil | S045 | I am planning for estate costs. Why would you deduct them from my monthly living cash? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-041 | Lower-income / hardship, 66, English | S020 | I plan to sell the flat and buy smaller. How much cash do I actually have after CPF refund? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-042 | Lower-income / hardship, 73, Mandarin | S032 | I plan to wait until age 70 for CPF payout. How do I pay my bills first? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-043 | PR and cross-border, 47, English | S038 | I want to retire in Johor. Can you show what you do not know about taxes or healthcare? | Block numerical inference; explain missing proof and offer general educational alternatives | PROTECTIVE_BLOCK |
| SIM-044 | PR and cross-border, 52, Malay | S039 | I hold MYR assets and SGD debt. Do you translate each at the same date? | Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations | DESIGN_SPECIFIED |
| SIM-045 | PR and cross-border, 56, Mandarin | S040 | I am moving back to Singapore. What does residency mean for my tax? | Block numerical inference; explain missing proof and offer general educational alternatives | PROTECTIVE_BLOCK |
| SIM-046 | PR and cross-border, 61, English | S041 | I receive a pension overseas. Are you assuming the full gross amount arrives? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-047 | PR and cross-border, 68, English | S043 | If I sell my business, please do not add its sale value on top of its existing valuation. | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |
| SIM-048 | PR and cross-border, 74, Mandarin | S046 | My company might fail. Do you assume I personally owe every company debt? | Show only confirmed components; request exact dated facts; flag missing terms and never infer them | CONDITIONAL_FACTS |

## Prioritised unresolved design findings

| Priority | Engine | Finding | Recommended rule |
|---|---|---|---|
| P0 | F01/F02 | Gross vs net income and multiple income streams | Separate employment gross wages, commissions, platform net earnings and SEP net trade income; recompute applicable contributions and taxes; no double-count. |
| P0 | F03/F04/F05 | CPF contributors must not be treated interchangeably | SC / PR year, employee vs platform worker opt-in, SEP NTT, earnings base and effective year must be selected. |
| P0 | F06 | CPF earnings and access are not equivalent to spending cash | Keep OA/SA/MA/RA distinct and model interest, age 55, withdrawals, property recredit, caps. |
| P0 | F07/S030 | Member-supplied CPF LIFE values need date and plan | Require official estimate source, plan, start age, capture date, no private payout inference; compare liquidity bridge and no forced advice. |
| P0 | F08/S020 | Property sale cash waterfall | Deduct mortgage, fees and CPF refund; reflect RA/OA credits separately and replacement funding, stamp duties, transaction timing. |
| P0 | F14 | Liquidity gap / decumulation order unresolved | Decide which sources may fund deficits, preserve reserve, prohibited CPF withdrawals, uncertain borrowing. |
| P0 | F16 | Unknown must never become zero | Mark missing financial facts as unknown and present conditional range or blocked computation. |
| P0 | F10/F16 | Nominal, real and inflation presentation | Base-date SGD nominal prices and separately deflated real values; show inflation on spending but not double-count returns. |
| P0 | F12/F11 | Care, health and insurance reimbursements | Add known costs; count only proven insurance/benefits in base case. |
| P0 | F01/F18 | Member ownership and family transition separation | Asset ownership, separate people and confirmed facts mandatory; divorce/death projections cannot assume transfers. |
| P1 | F13/F15 | Currency, foreign income and tax scope | Date FX and gross/net foreign pension; legal tax residency unverified must remain conditional. |
| P0 | Research quota | Research quota ages contradict role labels | Retirees 65+ and pre-retirees 55-64 must have compatible age slots. |
| P0 | Research validity | Synthetic simulation is not 48 consenting people | 48 hypothetical challenges are design checks only. No recruitment, consent, user observation or task success. |
| P0 | Consumer readability | Low-literacy and non-English comprehension cannot be assumed | Need tested understandable output, language versions and non-chart summaries for low digital confidence. |

## Product-owner decisions still required before calling specifications closed

| ID | Decision | Recommended default | Affected engines |
|---|---|---|---|
| D08 | Future statutory CPF policy for 2028+ | Recommend display explicit illustrative continuation of last known verified rates with scenario toggle and strong warning; never label as official future law | F03/F06 |
| D09 | How to fund a retirement cash shortfall | Recommend: spendable cash above reserve, then explicitly approved liquid assets; no forced sales, loans or restricted CPF | F14 |
| D10 | Planning horizon and mortality | Recommend show age 90, 95 and 100 survival horizons as scenarios, never a single assumed lifespan or prediction | F14/F16 |
| D11 | Property downsizing when replacement requires financing | Recommend show deficit and block affordability claim until actual mortgage facility and timing provided | F08/S020 |
| D12 | Unverified insurance / subsidy / inheritance | Recommend exclude from baseline, allow an optional separate clearly conditional scenario | F11/F17/F18 |
| D13 | FX and overseas rules | Recommend keep cross-border as documented cash-flow-only until each jurisdiction model is verified | F15 |
| D14 | Retirement confidence or readiness badges | Recommend show cash runway, goal shortfall and assumptions; no percentile or quantified confidence on 96 personas | F16 |
| D15 | Joint household finances under refused consent | Recommend calculate only confirmed individual-owned facts, show joint remainder as unknown; no spouse CPF/income guesses | F01/F16 |
| D16 | Scenario combination and double counting | Recommend event-sourcing by dated transaction and owner, with deterministic precedence and conflict notifications | All scenarios |

## Design acceptance conditions for Atlas handoff

1. Every financial rule accepts dated source and records whether it is official policy, confirmed user fact or planning assumption.
2. Each income stream remains separate and is taxed/CPF-processed according to its actual status. CPF is never counted as unrestricted cash.
3. Financial projections reconcile monthly source-to-use, account balances and transaction conservation; no partial-month or double-count errors.
4. All 46 scenario events are dated and owner-scoped; before/after differences are derived by recalculation, not a superficial percentage adjustment.
5. Unsupported government benefits, CPF LIFE estimates, insurance payouts, inheritance and property entitlements are excluded from base case, not set to arbitrary positive values.
6. At least 1 golden financial case + missing-input/refusal case per engine and 1 combined-effect conflict test per multi-engine scenario are required before marking build ready.
7. Consumer outputs show relevant shortfall, assumptions, money accessible versus locked, date of source and plain-language next fact needed. No persona confidence probability.
8. 48 simulated walkthroughs are design coverage only. A real 48-person study would still be required for actual consumer validation.

## Source registry

| Area | Authority | Reference URL | Role |
|---|---|---|---|
| CPF FRS 55 cohorts | Official CPF Board | https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum | 2026 FRS SGD 220,400; 2027 FRS SGD 228,200 |
| CPF employee rate bands | Official CPF Board | https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay | 2026 rates by age and PR cohort, 2027 revisions |
| CPF platform contributors | Official CPF Board | https://www.cpf.gov.sg/service/article/what-is-the-change-in-cpf-contribution-rates-for-platform-workers-from-january-2026 | Born 1995+ or opted in differ from pre-1995 non-opted in |
| CPF SEP MediSave | Official CPF Board | https://www.cpf.gov.sg/service/article/how-do-i-derive-my-medisave-contributions-amount-as-a-self-employed-person | NTI age/year based, excluding operator-reported platform income |
| CPF interest | Official CPF Board | https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates | 2026 Q4 OA 2.5%; SA/MA/RA 4% and age-tier extra interest |
| CPF 55 SA closure | Official CPF Board | https://www.cpf.gov.sg/service/article/what-is-the-closure-of-special-account-for-members-aged-55-and-above-about | SA closes and RA created at 55 for recent cohorts |
| CPF LIFE payout starts | Official CPF Board | https://www.cpf.gov.sg/service/article/when-can-i-start-receiving-my-cpf-life-payouts | Between 65 and 70; personalised member figure not generated |
| CPF official payout tools | Official CPF Board | https://www.cpf.gov.sg/service/article/what-are-the-different-features-found-in-the-retirement-payout-planner | Use member-provided official estimate |
| CPF housing sale refund | Official CPF Board | https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home/cpf-refund-when-selling-or-transferring-property | P+I CPF refund, conditional RA/OA allocation after sale |
| Singapore income tax | Official IRAS | https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates | Progressive resident rates, deductions/reliefs need fact checking |
