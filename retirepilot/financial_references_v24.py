"""Bounded, source-backed Singapore planning reference calculations.

None of these calculations establishes an official CPF, IRAS, HDB or legal determination.
Never use these outputs to silently overwrite user-reported cash flows.
"""
from __future__ import annotations
from decimal import Decimal
from .core import dec, money, ValidationError

SOURCE_TAX='https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates'
SOURCE_CPF_INTEREST='https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates'
SOURCE_INTEREST_TIMING='https://www.cpf.gov.sg/service/article/how-is-my-cpf-interest-computed-and-credited-into-my-accounts'
SOURCE_CPF_SALE='https://www.cpf.gov.sg/service/article/what-will-happen-to-my-sales-proceeds-after-the-sale-of-my-property'
SOURCE_REFUND='https://www.cpf.gov.sg/service/article/why-do-i-need-to-refund-the-accrued-interest-on-the-amount-of-cpf-savings-used-for-my-property'

# Source: IRAS current resident rates from YA2024 onward. Bounds are chargeable income, not gross income.
TAX_BRACKETS=(
    ('20000','0'),('30000','0.02'),('40000','0.035'),('80000','0.07'),
    ('120000','0.115'),('160000','0.15'),('200000','0.18'),('240000','0.19'),
    ('280000','0.195'),('320000','0.20'),('500000','0.22'),('1000000','0.23'),
    (None,'0.24')
)

def _review(reason, sources=None):
    return {'status':'requires_review','reason':reason,'sources':sources or []}

def resident_tax_reference(*, chargeable_income, year_of_assessment:int, resident_confirmed:bool,
                           chargeable_income_confirmed:bool, other_rebates_or_credits=None):
    """Tax *before* rebates/credits, if YA and assessed chargeable income are established.
    It cannot infer chargeable income from wages, commission or rental receipts.
    """
    if year_of_assessment not in (2026,2027):
        return _review('Only YA 2026/2027 reference cases reviewed; verify other YAs', [SOURCE_TAX])
    if resident_confirmed is not True or chargeable_income_confirmed is not True:
        return _review('Confirmed Singapore tax-residency and assessed chargeable income required',[SOURCE_TAX])
    if other_rebates_or_credits not in (None,0,'0'):
        return _review('Tax rebates and credits are excluded; use official IRAS assessment',[SOURCE_TAX])
    amount=dec(chargeable_income,'chargeable income')
    if amount<0:raise ValidationError('Chargeable income must not be negative')
    owed=Decimal(0);prev=Decimal(0)
    for limit,rate in TAX_BRACKETS:
        upper=dec(limit) if limit is not None else amount
        segment=max(Decimal(0),min(amount,upper)-prev)
        owed+=segment*dec(rate)
        if amount<=upper:break
        prev=upper
    return {'status':'bounded_reference','year_of_assessment':year_of_assessment,
            'chargeable_income_sgd':money(amount),'tax_before_rebates_sgd':money(owed),
            'sources':[SOURCE_TAX],
            'limitations':'Only IRAS resident progressive bracket calculation from confirmed chargeable income. No deduction/relief calculation, rebates, instalments, non-resident treatment or automatic cash-flow updates.'}

def static_cpf_interest_reference(*, age:int, balances:dict, as_of_quarter:str, 
                                  cpf_life_premium_balance=0, no_transactions_confirmed:bool=False):
    """Pure annualised unchanged-balance rate decomposition, not CPF's credited interest.
    Requires static balance assumption and published 2026 Q4 quarterly rates.
    """
    if as_of_quarter!='2026Q4':return _review('Only published 2026 Q4 interest-rate reference is included',[SOURCE_CPF_INTEREST])
    if no_transactions_confirmed is not True:return _review('Static balance, no-contributions/withdrawals assumption required',[SOURCE_INTEREST_TIMING])
    if not isinstance(age,int) or age<0:return _review('Valid age required',[SOURCE_CPF_INTEREST])
    if cpf_life_premium_balance not in (0,'0',None):return _review('CPF LIFE premium interest needs official model',[SOURCE_CPF_INTEREST])
    if not isinstance(balances,dict) or any(x not in ('OA','SA','MA','RA') for x in balances):raise ValidationError('Invalid CPF account list')
    if not balances:return _review('Actual CPF balances required',[SOURCE_CPF_INTEREST])
    b={k:dec(balances.get(k,0),k) for k in ('OA','SA','MA','RA')}
    if any(v<0 for v in b.values()):raise ValidationError('CPF balances cannot be negative')
    if age>=55 and b['SA']>0:return _review('SA closure at 55 is not reconciled; verify actual account statement',[SOURCE_CPF_INTEREST])
    base=b['OA']*Decimal('.025')+(b['SA']+b['MA']+b['RA'])*Decimal('.04')
    # Official ordering for allocation of extra-interest eligible balances: RA, OA (capped 20k), SA, MA.
    eligible=[('RA',b['RA']),('OA',min(b['OA'],Decimal(20000))),('SA',b['SA']),('MA',b['MA'])]
    available=Decimal(60000);top=Decimal(30000);extra=Decimal(0)
    for name,amt in eligible:
        covered=min(available,amt)
        if age>=55:
            high=min(top,covered)
            extra+=high*Decimal('.02')+(covered-high)*Decimal('.01')
            top-=high
        else:extra+=covered*Decimal('.01')
        available-=covered
        if available<=0:break
    return {'status':'illustrative_static_balance_reference','quarter':'2026Q4','age':age,
            'base_interest_annualised_sgd':money(base),'extra_interest_annualised_sgd':money(extra),
            'total_interest_annualised_sgd':money(base+extra),
            'sources':[SOURCE_CPF_INTEREST,SOURCE_INTEREST_TIMING],
            'limitations':'Rate-only illustration for constant unchanged balances. Official CPF interest is computed monthly and credited annually; this does NOT simulate contribution timing, account transitions at 55, CPF LIFE premium or future rates.'}

def housing_sale_reference(*, sale_price, outstanding_loan, required_cpf_refund, sale_costs,
                           property_rule_class:str, official_refund_confirmed:bool):
    """Simple positive-surplus waterfall using official/user-verified accrued CPF refund.
    Does not estimate the amount or timing of CPF accrued interest.
    """
    if property_rule_class not in ('hdb','private_post_2002'):
        return _review('Pre-2002 and other sale priorities require case-specific official assessment',[SOURCE_CPF_SALE])
    if official_refund_confirmed is not True:
        return _review('Official required CPF refund including accrued interest must be confirmed',[SOURCE_REFUND])
    price=dec(sale_price,'sale price');loan=dec(outstanding_loan,'outstanding loan')
    refund=dec(required_cpf_refund,'official CPF refund');cost=dec(sale_costs,'sale costs')
    if any(z<0 for z in (price,loan,refund,cost)):raise ValidationError('Negative property sale input')
    if price<loan:return _review('Sale proceeds insufficient to repay housing loan; contractual/lender review needed',[SOURCE_CPF_SALE])
    after_loan=price-loan
    cpf_return=min(after_loan,refund)
    after_cpf=after_loan-cpf_return
    if after_cpf<cost:return _review('Sale proceeds insufficient for supplied sale costs; professional review needed',[SOURCE_CPF_SALE])
    return {'status':'bounded_reference','sale_price_sgd':money(price),
            'loan_repaid_sgd':money(loan),'cpf_refund_sgd':money(cpf_return),
            'requested_cpf_refund_sgd':money(refund),'selling_costs_sgd':money(cost),
            'cash_sale_proceeds_sgd':money(after_cpf-cost),
            'sources':[SOURCE_CPF_SALE,SOURCE_REFUND],
            'limitations':'Only simplified waterfall for HDB or post-2002 private sale, with supplied official refund and costs; no CPF RA transfer, owner splits, option money, agent fees/tax or legal completion review.'}

def employee_cpf_schedule_2026_27(*, dob:str, residency:str, pr_cpf_year,
                                   months_and_wages:list):
    """Reconcile a series of 2026/27 OW-only amounts; no allocations/interest/CPF LIFE.
    Each monthly value must independently meet the underlying official Table 1 constraints.
    """
    from .statutory_2026 import employee_ow_cpf
    if not isinstance(months_and_wages,list) or not months_and_wages or len(months_and_wages)>24:
        raise ValidationError('1 to 24 calendar-month observations required')
    seen=set();results=[]
    for item in months_and_wages:
        if not isinstance(item,dict) or item.get('month') in seen:
            raise ValidationError('Each unique month must be an object')
        seen.add(item.get('month'))
        result=employee_ow_cpf(dob=dob,residency=residency,pr_cpf_year=pr_cpf_year,
                                month=item['month'],monthly_ordinary_wages=item['ordinary_wages'])
        if result['status']!='bounded_reference':
            return _review('Schedule blocked: '+result['reason'],[result.get('source','')])
        results.append(result)
    return {'status':'bounded_reference','months_count':len(results),'months':results,
            'worker_total_sgd':money(sum(dec(x['worker_share_sgd']) for x in results)),
            'employer_total_sgd':money(sum(dec(x['employer_share_sgd']) for x in results)),
            'sources':[x['source'] for x in results],
            'limitations':'Bounded 2026/27 employee OW-only reference; not full-year CPF ceiling, allocations, interest, withdrawals or CPF LIFE calculation. No automatic forecast overwrite.'}
