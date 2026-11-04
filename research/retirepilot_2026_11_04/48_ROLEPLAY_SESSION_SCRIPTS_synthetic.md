# RetirePilot: 48 Simulated Consumer Review Sessions
**Synthetic tabletop scripts only. No real participants, interviews, observed task completions, signed consent or real financial records.**
**Review date:** 2026-11-04. **Purpose:** Clarify expected financial and scenario logic before Atlas builds.

## Session interpretation
Each session is a hypothetical first-person challenge from a distinct fictional Singapore citizen/PR persona. The product response is a proposed business rule, not observed software behaviour. Cases ending in refusal may still be design-correct.

### SIM-001 | Salaried households | Age 45 | Citizen | English | S001 Retrenchment
**Synthetic context:** Illustrative wages S$6,100/month; housing debt and CPF balances unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My company is letting me go. Can you tell me how long my cash will last before CPF starts?”
**Expected assistant business response (not an actual product output):** “I would end affected salary on verified date, keep other streams, stop linked contributions; add severance only when confirmed. However, no default retrenchment benefit, CPF/pension income not invented. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-002 | Salaried households | Age 48 | Citizen | Mandarin | S002 Pay reduction
**Synthetic context:** Illustrative wages S$4,900/month; housing debt and CPF balances unknown. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “My company cut my salary by a quarter. Is the impact on take-home cash the same?”
**Expected assistant business response (not an actual product output):** “I would apply updated effective-date income; recalc employee CPF and tax from gross amount. However, do not subtract gross cut as though it were net spending cash. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-003 | Salaried households | Age 51 | Citizen | English | S003 Contract non-renewal
**Synthetic context:** Illustrative wages S$6,100/month; housing debt and CPF balances unknown. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “My contract ends in March. Do I keep CPF and income in your forecast after that?”
**Expected assistant business response (not an actual product output):** “I would end fixed-term wage and contributions on stated contract end; bridge with documented available liquidity. However, do not presume renewal or severance. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-004 | Salaried households | Age 56 | PR | Malay | S004 Reduced working hours
**Synthetic context:** Illustrative wages S$5,700/month; housing debt and CPF balances unknown. Housing: Renting. Digital confidence: Low.
**Consumer:** “I want to work three days a week. What changes besides the monthly pay?”
**Expected assistant business response (not an actual product output):** “I would replace current earned income and working hours for dated period; recompute linked CPF/tax and bridge. However, current v2.8 preview only net earned-cash sensitivity. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-005 | Salaried households | Age 60 | Citizen | English | S005 Delayed retirement
**Synthetic context:** Illustrative wages S$4,900/month; housing debt and CPF balances unknown. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “If I work until 68 instead of 63, do you assume the company keeps me?”
**Expected assistant business response (not an actual product output):** “I would shift planned stop-work age later; extend wages/CPF accrual by employment type. However, no guarantee of employment continuation. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-006 | Salaried households | Age 64 | Citizen | Tamil | S006 Return to work
**Synthetic context:** Illustrative wages S$6,500/month; housing debt and CPF balances unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I am taking another job in retirement. Does this stop my CPF LIFE?”
**Expected assistant business response (not an actual product output):** “I would insert dated new job stream and correct contribution scheme; leave CPF LIFE payments untouched absent official change. However, do not assume rehiring, salary or pension suspension. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-007 | Platform and gig workers | Age 45 | Citizen | English | S007 Commission -50%
**Synthetic context:** Illustrative net platform cash S$2,300/month; opt-in / operator contributions must be established. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My commissions fell by half, but my base salary did not. Which figure changes?”
**Expected assistant business response (not an actual product output):** “I would apply commission drop only to affected commission stream and re-evaluate costs, tax and SEP MediSave. However, never haircut all household income. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-008 | Platform and gig workers | Age 49 | Citizen | Malay | S008 Platform suspension
**Synthetic context:** Illustrative net platform cash S$3,700/month; opt-in / operator contributions must be established. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “My ride-hail account is suspended. Does the app still count my other delivery work?”
**Expected assistant business response (not an actual product output):** “I would zero dated platform net earnings for affected operator; recompute platform CPF contributions. However, other platform/non-platform streams continue. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-009 | Platform and gig workers | Age 51 | PR | Mandarin | S009 Declining orders
**Synthetic context:** Illustrative net platform cash S$2,650/month; opt-in / operator contributions must be established. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “I get fewer orders, but the platform fees vary. Are you using gross or net?”
**Expected assistant business response (not an actual product output):** “I would recalculate net orders * net per order after fees; capture date range. However, volume shock is not equivalent to gross revenue shock. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-010 | Platform and gig workers | Age 55 | Citizen | Tamil | S010 Vehicle operating-cost shock
**Synthetic context:** Illustrative net platform cash S$2,300/month; opt-in / operator contributions must be established. Housing: Renting. Digital confidence: Low.
**Consumer:** “Petrol and vehicle repairs have jumped. You are not subtracting them twice, right?”
**Expected assistant business response (not an actual product output):** “I would change dated vehicle operating expenses in correct stream; recalc net cash and relevant assessed income. However, ensure no second deduction under household expenses. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-011 | Platform and gig workers | Age 61 | Citizen | English | S011 Loss of major client
**Synthetic context:** Illustrative net platform cash S$2,650/month; opt-in / operator contributions must be established. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “One client provides most of my income. If they leave, what other income remains?”
**Expected assistant business response (not an actual product output):** “I would stop or reduce identified client stream with contractual notice/replacement assumptions. However, do not apply portfolio-wide income haircut. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-012 | Platform and gig workers | Age 68 | Citizen | Malay | S033 Contribution interruption
**Synthetic context:** Illustrative net platform cash S$3,350/month; opt-in / operator contributions must be established. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I took six months off work. Does the CPF forecast still give me salary contributions?”
**Expected assistant business response (not an actual product output):** “I would suspend contributor-specific CPF postings for verified months; recompute full cash/payroll interactions. However, never assume CPF contributions continue after income stops. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-013 | Self-employed / property agents | Age 47 | Citizen | Mandarin | S018 Mortgage repricing
**Synthetic context:** Illustrative variable net trade income S$5,100/month; business expenses and assessed NTI require evidence. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My mortgage goes from 2.6% to 4%. Will you keep the same loan term?”
**Expected assistant business response (not an actual product output):** “I would amortize existing housing loan with new rate from reset date and actual remaining term. However, repricing does not refinance automatically. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-014 | Self-employed / property agents | Age 50 | Citizen | English | S019 Property-value decline
**Synthetic context:** Illustrative variable net trade income S$3,700/month; business expenses and assessed NTI require evidence. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “My HDB value drops. Does your chart think cash left my bank account?”
**Expected assistant business response (not an actual product output):** “I would update property fair value and secured-equity estimate, leave cash and loan principal unchanged. However, loss of net worth is not immediate cash outflow. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-015 | Self-employed / property agents | Age 54 | Citizen | English | S020 Downsizing
**Synthetic context:** Illustrative variable net trade income S$6,500/month; business expenses and assessed NTI require evidence. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “I plan to sell the flat and buy smaller. How much cash do I actually have after CPF refund?”
**Expected assistant business response (not an actual product output):** “I would sale proceeds less settlement/fees/CPF refund; separate OA/RA credits; replacement purchase, duties, bridge, new loan flows. However, cPF refunds are not available cash; eligibility and timing must be confirmed. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-016 | Self-employed / property agents | Age 58 | Citizen | Malay | S021 Rent increase
**Synthetic context:** Illustrative variable net trade income S$5,800/month; business expenses and assessed NTI require evidence. Housing: Renting. Digital confidence: Low.
**Consumer:** “My landlord raised rent in July. Does the higher amount begin only then?”
**Expected assistant business response (not an actual product output):** “I would dated rent reset changes cash expense; apply deposits and moving fees only when provided. However, avoid retroactive rent changes. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-017 | Self-employed / property agents | Age 62 | Citizen | Mandarin | S022 Lease monetisation
**Synthetic context:** Illustrative variable net trade income S$5,100/month; business expenses and assessed NTI require evidence. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “If I join the Lease Buyback Scheme, can you calculate benefits without an HDB quote?”
**Expected assistant business response (not an actual product output):** “I would use official scheme eligibility and quote, including lease, RA and proceeds, then model dated receipts. However, no estimated HDB Lease Buyback entitlement. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Block numerical inference; explain missing proof and offer general educational alternatives. **Scenario outcome:** PROTECTIVE_BLOCK.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-018 | Self-employed / property agents | Age 67 | Citizen | English | S023 Rental vacancy
**Synthetic context:** Illustrative variable net trade income S$5,100/month; business expenses and assessed NTI require evidence. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My investment property is empty three months. Do mortgage costs continue?”
**Expected assistant business response (not an actual product output):** “I would zero rent only in vacancy months but keep mortgage/tax/maintenance and vacancy expenses. However, rental loss not property valuation loss. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-019 | Pre-retirees | Age 55 | PR | English | S024 Equity market decline
**Synthetic context:** Illustrative liquid savings S$90,000; CPF payout amount not assumed. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “Markets crash 20%. Do you assume it all comes back next year?”
**Expected assistant business response (not an actual product output):** “I would apply dated drawdown by asset class with liquidity conditions; continue portfolio path without assumed recovery. However, no guaranteed bounce-back. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-020 | Pre-retirees | Age 57 | Citizen | Mandarin | S025 Low real returns
**Synthetic context:** Illustrative liquid savings S$142,000; CPF payout amount not assumed. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “I am worried about inflation. Are these real returns or nominal returns?”
**Expected assistant business response (not an actual product output):** “I would apply real-return sensitivity to explicit nominal return and inflation paths per asset. However, do not subtract inflation twice. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-021 | Pre-retirees | Age 59 | Citizen | Malay | S026 Poor early withdrawal returns
**Synthetic context:** Illustrative liquid savings S$194,000; CPF payout amount not assumed. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “What if the market crashes early while I am drawing retirement income?”
**Expected assistant business response (not an actual product output):** “I would apply ordered path of early losses and withdrawals; recompute end capital and reserve. However, sequence of returns matters, not just average return. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-022 | Pre-retirees | Age 61 | Citizen | English | S027 Concentrated stock loss
**Synthetic context:** Illustrative liquid savings S$116,000; CPF payout amount not assumed. Housing: Renting. Digital confidence: Low.
**Consumer:** “My single stock position falls 70%. Why is the whole portfolio down 70%?”
**Expected assistant business response (not an actual product output):** “I would apply shock to named concentrated holding and denominator of total portfolio. However, not a shock to entire investments. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-023 | Pre-retirees | Age 63 | Citizen | Tamil | S028 Inflation shock
**Synthetic context:** Illustrative liquid savings S$168,000; CPF payout amount not assumed. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “Healthcare inflation could outpace general inflation. Can I set that separately?”
**Expected assistant business response (not an actual product output):** “I would apply category-specific expense and income indexing assumptions by dates. However, do not equate inflation to investment loss. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-024 | Pre-retirees | Age 64 | Citizen | English | S029 Earlier retirement
**Synthetic context:** Illustrative liquid savings S$194,000; CPF payout amount not assumed. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I stop work at 60. Why does CPF LIFE not start until later?”
**Expected assistant business response (not an actual product output):** “I would move wage stop date earlier; recompute contributions and explicit liquidity bridge to official payout age. However, cPF LIFE start not moved earlier by early employment exit. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-025 | Retirees | Age 65 | Citizen | English | S030 Payout deferral
**Synthetic context:** Illustrative non-CPF household costs S$1,700/month; member-specific CPF estimate not invented. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “CPF shows different estimates if I start at 65 or 70. Can I compare both and the cash gap?”
**Expected assistant business response (not an actual product output):** “I would compare separate member-provided official payout scenarios from 65/70 and bridging cash needs. However, no automatic best-age advice or generic uplift as personal quote. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-026 | Retirees | Age 66 | Citizen | Mandarin | S031 Voluntary top-up
**Synthetic context:** Illustrative non-CPF household costs S$1,950/month; member-specific CPF estimate not invented. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “If I top up RA, how do you know my actual payout will increase?”
**Expected assistant business response (not an actual product output):** “I would reallocate confirmed available cash/OA to RA under verified limits; revise payout only with new official member estimate. However, do not award assumed tax relief or payout increase. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-027 | Retirees | Age 69 | Citizen | English | S032 Pre-payout funding bridge
**Synthetic context:** Illustrative non-CPF household costs S$2,700/month; member-specific CPF estimate not invented. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “I plan to wait until age 70 for CPF payout. How do I pay my bills first?”
**Expected assistant business response (not an actual product output):** “I would calculate dated cash bridge until actual member-provided payout start; report reserve exhaustion. However, cannot withdraw restricted CPF to plug deficit. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-028 | Retirees | Age 71 | Citizen | Malay | S034 Medical expense shock
**Synthetic context:** Illustrative non-CPF household costs S$1,950/month; member-specific CPF estimate not invented. Housing: Renting. Digital confidence: Low.
**Consumer:** “I may need a medical procedure. Do you count my insurance reimbursement automatically?”
**Expected assistant business response (not an actual product output):** “I would schedule immediate/recurring out-of-pocket cost and only verified reimbursements. However, never assume insurance coverage pays. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-029 | Retirees | Age 74 | Citizen | English | S035 Disability-related cost shock
**Synthetic context:** Illustrative non-CPF household costs S$2,700/month; member-specific CPF estimate not invented. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “Disability costs may rise and I may earn less. Are those separate assumptions?”
**Expected assistant business response (not an actual product output):** “I would separate disabled-person spending, reduced wages and confirmed benefits into distinct dated streams. However, do not infer disability-benefit eligibility. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-030 | Retirees | Age 78 | Citizen | Tamil | S036 Long-term care expense
**Synthetic context:** Illustrative non-CPF household costs S$2,450/month; member-specific CPF estimate not invented. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “Care may get more expensive over time. Can you avoid assuming subsidies?”
**Expected assistant business response (not an actual product output):** “I would use staged care intensity, care period, out-of-pocket burden and documented payout policy. However, do not presume policy eligibility or care duration. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-031 | Family and caregivers | Age 46 | Citizen | English | S012 Divorce
**Synthetic context:** Illustrative family expenses S$4,400/month; financial ownership and transfers not presumed. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “We are separating. Please do not assume half the flat or my spouse CPF belongs to me.”
**Expected assistant business response (not an actual product output):** “I would model separate households after documented separation dates and agreed financial obligations only. However, block property division, maintenance, CPF or custody assumptions without actual terms. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Block numerical inference; explain missing proof and offer general educational alternatives. **Scenario outcome:** PROTECTIVE_BLOCK.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-032 | Family and caregivers | Age 50 | Citizen | Tamil | S013 Widowhood
**Synthetic context:** Illustrative family expenses S$3,700/month; financial ownership and transfers not presumed. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “My partner died. Will you automatically assume I get all their CPF and insurance?”
**Expected assistant business response (not an actual product output):** “I would on verified death event stop deceased income; introduce only confirmed survivors benefits, claims and estate receipts. However, do not assume inheritance/insurance payouts, spouse CPF rights. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-033 | Family and caregivers | Age 54 | Citizen | Mandarin | S014 New child/dependant
**Synthetic context:** Illustrative family expenses S$3,000/month; financial ownership and transfers not presumed. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “Our family is adding a dependent. Will childcare grants already be counted?”
**Expected assistant business response (not an actual product output):** “I would introduce dated newborn/dependant recurring and one-time costs, medical and education. However, benefits and grants conditional until confirmed. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-034 | Family and caregivers | Age 58 | Citizen | English | S015 Adult child support
**Synthetic context:** Illustrative family expenses S$4,400/month; financial ownership and transfers not presumed. Housing: Renting. Digital confidence: Low.
**Consumer:** “I support an adult child for two years. Can I set a definite end date?”
**Expected assistant business response (not an actual product output):** “I would add timed adult-child support; distinguish loan vs grant and one-time vs recurring. However, avoid implied permanent support or double counting. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-035 | Family and caregivers | Age 62 | Citizen | Malay | S016 Parent care
**Synthetic context:** Illustrative family expenses S$3,700/month; financial ownership and transfers not presumed. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “My mother needs help. Will you count her CareShield LIFE payout without proof?”
**Expected assistant business response (not an actual product output):** “I would add parent care cost, time off and separate wage impact; reflect verified subsidies/insurance only. However, no automatic CareShield or MediSave reimbursement assumption. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-036 | Family and caregivers | Age 71 | Citizen | Mandarin | S017 Loss of second income
**Synthetic context:** Illustrative family expenses S$4,750/month; financial ownership and transfers not presumed. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My spouse will stop working. Does that affect only one person’s income and CPF?”
**Expected assistant business response (not an actual product output):** “I would remove second adult stream on dated trigger and linked CPF/tax while preserving other adult data boundaries. However, do not delete assets or assume spouse resources inaccessible. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-037 | Lower-income / hardship | Age 45 | Citizen | Malay | S037 Caregiver income loss
**Synthetic context:** Illustrative net cash S$1,100/month; affordability and government support unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I might leave work to care for family. Does the plan assume the government pays my salary?”
**Expected assistant business response (not an actual product output):** “I would stop/reduce caregiver earned income for documented leave; add support cost separately. However, no automatic statutory leave compensation. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-038 | Lower-income / hardship | Age 51 | PR | English | S042 Inheritance
**Synthetic context:** Illustrative net cash S$1,300/month; affordability and government support unknown. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “My parent’s estate is unresolved. Can I leave the inheritance out until it arrives?”
**Expected assistant business response (not an actual product output):** “I would post confirmed net inheritance receipt after probate, costs and actual ownership transfer. However, pending estate is not available cash. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-039 | Lower-income / hardship | Age 56 | Citizen | Mandarin | S044 Major gift to children
**Synthetic context:** Illustrative net cash S$1,300/month; affordability and government support unknown. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “I want to give my daughter cash, but it must come from accessible savings.”
**Expected assistant business response (not an actual product output):** “I would reduce spendable liquid assets on dated cash gift, reflect other household only when ownership known. However, do not gift restricted CPF balances. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-040 | Lower-income / hardship | Age 60 | Citizen | Tamil | S045 Estate expense
**Synthetic context:** Illustrative net cash S$1,100/month; affordability and government support unknown. Housing: Renting. Digital confidence: Low.
**Consumer:** “I am planning for estate costs. Why would you deduct them from my monthly living cash?”
**Expected assistant business response (not an actual product output):** “I would book documented estate/probate expenses against correct paying estate/member. However, do not charge a living member for hypothetical estate costs. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-041 | Lower-income / hardship | Age 66 | Citizen | English | S020 Downsizing
**Synthetic context:** Illustrative net cash S$1,300/month; affordability and government support unknown. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “I plan to sell the flat and buy smaller. How much cash do I actually have after CPF refund?”
**Expected assistant business response (not an actual product output):** “I would sale proceeds less settlement/fees/CPF refund; separate OA/RA credits; replacement purchase, duties, bridge, new loan flows. However, cPF refunds are not available cash; eligibility and timing must be confirmed. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-042 | Lower-income / hardship | Age 73 | Citizen | Mandarin | S032 Pre-payout funding bridge
**Synthetic context:** Illustrative net cash S$1,700/month; affordability and government support unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I plan to wait until age 70 for CPF payout. How do I pay my bills first?”
**Expected assistant business response (not an actual product output):** “I would calculate dated cash bridge until actual member-provided payout start; report reserve exhaustion. However, cannot withdraw restricted CPF to plug deficit. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-043 | PR and cross-border | Age 47 | PR | English | S038 Retire overseas
**Synthetic context:** Illustrative foreign assets or income S$110,000 equivalent; actual FX, residency and obligations unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “I want to retire in Johor. Can you show what you do not know about taxes or healthcare?”
**Expected assistant business response (not an actual product output):** “I would combine location-specific cost, FX, foreign pensions, residency/tax status and healthcare. However, block jurisdiction-specific unsupported rules. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Block numerical inference; explain missing proof and offer general educational alternatives. **Scenario outcome:** PROTECTIVE_BLOCK.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-044 | PR and cross-border | Age 52 | PR | Malay | S039 Exchange-rate movement
**Synthetic context:** Illustrative foreign assets or income S$82,000 equivalent; actual FX, residency and obligations unknown. Housing: HDB owner. Digital confidence: Limited.
**Consumer:** “I hold MYR assets and SGD debt. Do you translate each at the same date?”
**Expected assistant business response (not an actual product output):** “I would revalue each foreign-currency asset, liability and recurring receipt using dated FX path. However, do not treat unrealised FX change as cash realised. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Use correctly dated, member-supplied shock on appropriate income/asset/cost streams, show before/after and limitations. **Scenario outcome:** DESIGN_SPECIFIED.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-045 | PR and cross-border | Age 56 | PR | Mandarin | S040 Repatriation
**Synthetic context:** Illustrative foreign assets or income S$40,000 equivalent; actual FX, residency and obligations unknown. Housing: Private mortgage. Digital confidence: Moderate.
**Consumer:** “I am moving back to Singapore. What does residency mean for my tax?”
**Expected assistant business response (not an actual product output):** “I would end offshore and start onshore incomes/costs with relocation expenses and tax residency changes. However, residency rights and tax effects must be documented. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Block numerical inference; explain missing proof and offer general educational alternatives. **Scenario outcome:** PROTECTIVE_BLOCK.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-046 | PR and cross-border | Age 61 | PR | English | S041 Foreign pension change
**Synthetic context:** Illustrative foreign assets or income S$110,000 equivalent; actual FX, residency and obligations unknown. Housing: Renting. Digital confidence: Low.
**Consumer:** “I receive a pension overseas. Are you assuming the full gross amount arrives?”
**Expected assistant business response (not an actual product output):** “I would enter verified foreign pension gross/net and indexation rules with FX and withholding. However, no unverified foreign pension entitlement. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-047 | PR and cross-border | Age 68 | PR | English | S043 Business sale
**Synthetic context:** Illustrative foreign assets or income S$110,000 equivalent; actual FX, residency and obligations unknown. Housing: HDB owner. Digital confidence: Moderate.
**Consumer:** “If I sell my business, please do not add its sale value on top of its existing valuation.”
**Expected assistant business response (not an actual product output):** “I would book verified sale proceeds after debt/fees and stop business earnings/equity upon closing. However, avoid double-counting business value and sale proceeds. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.

### SIM-048 | PR and cross-border | Age 74 | PR | Mandarin | S046 Business failure
**Synthetic context:** Illustrative foreign assets or income S$96,000 equivalent; actual FX, residency and obligations unknown. Housing: HDB owner. Digital confidence: Confident.
**Consumer:** “My company might fail. Do you assume I personally owe every company debt?”
**Expected assistant business response (not an actual product output):** “I would cease business revenue, write down business equity, include documented personal guarantees/liabilities. However, do not automatically transfer company debt to individual. If your source data is missing I will mark the affected value unknown, not zero.”
**Consumer follow-up:** “Which exact figures do I need to confirm, what money can I actually spend, and what parts of the forecast remain only assumptions?”
**Review criterion:** Show only confirmed components; request exact dated facts; flag missing terms and never infer them. **Scenario outcome:** CONDITIONAL_FACTS.
**Evidence:** Scripted model judgement only; no comprehension rating, no real session, no tested app response.
