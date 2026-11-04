"""Versioned, bounded CPF computations for a *synthetic* Singapore research prototype.

Does not replace CPF's official calculator or cover all contribution/eligibility cases.
Calculated values are for checking user-provided records and MUST NOT silently flow
into the household cash-flow forecast. Values are not payment instructions.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from .core import dec, money, age_on

SOURCE_EMPLOYEE_2026='https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay'
SOURCE_EMPLOYEE_2027='https://www.cpf.gov.sg/service/article/what-are-the-changes-to-the-cpf-contribution-rates-for-senior-workers-that-will-take-effect-from-1-january-2027'
SOURCE_ROUND='https://www.cpf.gov.sg/service/article/are-cpf-contributions-rounded-to-the-nearest-dollar'
SOURCE_PLATFORM_2026='https://www.cpf.gov.sg/service/article/what-is-the-change-in-cpf-contribution-rates-for-platform-workers-from-january-2026'
SOURCE_PLATFORM_ROUND='https://www.cpf.gov.sg/service/article/are-cpf-contributions-for-platform-workers-rounded-to-the-nearest-dollar'
SOURCE_FEDA='https://www.cpf.gov.sg/service/article/what-is-the-fixed-expense-deduction-amount'
SOURCE_SEP_2026='https://www.cpf.gov.sg/service/sfc/servlet.shepherd/document/download/069IW00000G4S1QYAV'
SOURCE_CPF_LIFE='https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month'

RATE_EMPLOYEE={
    2026:[('55',Decimal('17'),Decimal('20')),('60',Decimal('16'),Decimal('18')),('65',Decimal('12.5'),Decimal('12.5')),('70',Decimal('9'),Decimal('7.5')),('older',Decimal('7.5'),Decimal('5'))],
    2027:[('55',Decimal('17'),Decimal('20')),('60',Decimal('16.5'),Decimal('19')),('65',Decimal('13'),Decimal('13')),('70',Decimal('9'),Decimal('7.5')),('older',Decimal('7.5'),Decimal('5'))]
}
PW_OPTED=[(35,Decimal('7'),Decimal('13')),(45,Decimal('7'),Decimal('14')),(50,Decimal('7'),Decimal('15')),(55,Decimal('7'),Decimal('15.5')),(60,Decimal('7'),Decimal('15.5')),(65,Decimal('7'),Decimal('12.5')),(70,Decimal('7'),Decimal('9.5')),(999,Decimal('7'),Decimal('5.5'))]
PW_NOT_OPTED=[(35,Decimal('0'),Decimal('8')),(45,Decimal('0'),Decimal('9')),(50,Decimal('0'),Decimal('10')),(999,Decimal('0'),Decimal('10.5'))]
FEDA={'car':Decimal('60'),'van':Decimal('60'),'lorry':Decimal('60'),'truck':Decimal('60'),
      'motorcycle':Decimal('35'),'power_assisted_bicycle':Decimal('35'),
      'bicycle':Decimal('20'),'walk':Decimal('20')}


def _blocked(reason,source=None):
    out={'status':'requires_review','reason':reason}
    if source:out['source']=source
    return out

def _round_total(amount):return amount.quantize(Decimal('1'),rounding=ROUND_HALF_UP)
def _floor_worker(amount):return amount.quantize(Decimal('1'),rounding=ROUND_FLOOR)

def _band_index(dob:str,year:int,month:int,cutoffs:list[int]) -> int:
    """Age band changes in the month AFTER the corresponding birthday month."""
    born=date.fromisoformat(dob)
    start=date(year,month,1)
    for i,threshold in enumerate(cutoffs):
        birthday=date(born.year+threshold,born.month,born.day)
        # Previous month birthday is fully over at the start of current month.
        if start <= birthday.replace(day=1):return i
    return len(cutoffs)

def employee_ow_cpf(*,dob:str,residency:str,month:str,monthly_ordinary_wages,pr_cpf_year=None,
                    additional_wages=None,monthly_pr_rate_election=None) -> dict:
    """2026/27 Table 1 SG / third+ year PR, regular monthly OW, strictly >750 band.

    Treats rates as cohort/earnings reference: no AW ceiling, partial-month/payroll
    reconciliation, CPF allocations, or multiple-employer annual aggregation.
    """
    try:period=date.fromisoformat(month+'-01')
    except (ValueError,TypeError):return _blocked('month must be YYYY-MM',SOURCE_EMPLOYEE_2026)
    if period.year not in RATE_EMPLOYEE:return _blocked('Supported employee CPF reference years: 2026 and 2027 only',SOURCE_EMPLOYEE_2027)
    if residency not in ('SG','PR'):return _blocked('Employee CPF reference is for Singapore citizens or eligible PRs',SOURCE_EMPLOYEE_2026)
    if residency=='PR' and (pr_cpf_year is None or int(pr_cpf_year)<3):return _blocked('First/second-year PR graduated rates or elective full rates require separate official rules',SOURCE_EMPLOYEE_2026)
    if additional_wages not in (None,'0',0):return _blocked('Additional wages / annual wage ceiling not modelled; use official calculator',SOURCE_EMPLOYEE_2026)
    pay=dec(monthly_ordinary_wages,'monthly ordinary wages')
    if pay<0:return _blocked('Negative ordinary wages are not allowed')
    if pay<=Decimal('750'):return _blocked('CPF lower earnings tiers of $750 or less require separate official tables',SOURCE_EMPLOYEE_2026)
    idx=_band_index(dob,period.year,period.month,[55,60,65,70])
    band,employer_pct,worker_pct=RATE_EMPLOYEE[period.year][idx]
    assessable=min(pay,Decimal('8000'))
    worker=_floor_worker(assessable*worker_pct/100)
    total=_round_total(assessable*(employer_pct+worker_pct)/100)
    return {'status':'bounded_reference','month':month,'rule_year':period.year,'cpf_wage_type':'ordinary_wages_only',
            'assessable_wages_sgd':money(assessable),'gross_wages_sgd':money(pay),
            'employer_rate_pct':str(employer_pct),'worker_rate_pct':str(worker_pct),
            'worker_share_sgd':money(worker),'employer_share_sgd':money(total-worker),'total_cpf_sgd':money(total),
            'source':SOURCE_EMPLOYEE_2026 if period.year==2026 else SOURCE_EMPLOYEE_2027,
            'rounding_source':SOURCE_ROUND,'limitations':'Not official payroll computation; OW-only, >750 tier, no AW, no 1st/2nd-year PR, no CPF account allocation or annual cap reconciliation.'}

def platform_cpf(*,dob:str,month:str,monthly_gross,transport:str,opted_in,qualifying_platform_worker=True)->dict:
    """2026 single-operator monthly reference, strictly >750 statutory net earnings."""
    try: period=date.fromisoformat(month+'-01')
    except (ValueError,TypeError):return _blocked('month must be YYYY-MM')
    if period.year!=2026:return _blocked('Platform CPF monetary reference implemented for 2026 only',SOURCE_PLATFORM_2026)
    if not qualifying_platform_worker:return _blocked('Qualifying platform agreement/control not established',SOURCE_PLATFORM_2026)
    if transport not in FEDA:return _blocked('Transport mode missing or unsupported; FEDA cannot be inferred',SOURCE_FEDA)
    gross=dec(monthly_gross,'gross platform earnings')
    if gross<0:return _blocked('Gross earnings must be non-negative')
    net=gross*(Decimal(100)-FEDA[transport])/100
    if net<=750:return _blocked('Net earnings at or below $750 use other contribution tiers',SOURCE_PLATFORM_2026)
    born=date.fromisoformat(dob)
    if born<date(1995,1,1) and opted_in is None:return _blocked('Pre-1995 worker opt-in status unknown; verify with CPF',SOURCE_PLATFORM_2026)
    increased=born>=date(1995,1,1) or opted_in is True
    bandlist=PW_OPTED if increased else PW_NOT_OPTED
    # CPF defines the next age group from the month following the birthday.
    effective_age=age_on(dob,period)
    cutoff_idx=_band_index(dob,period.year,period.month,[x[0] for x in bandlist[:-1]])
    operator_pct,worker_pct=bandlist[cutoff_idx][1:]
    if increased:
        worker=_floor_worker(net*worker_pct/100)
        total=_round_total(net*(operator_pct+worker_pct)/100)
        operator=total-worker
    else:
        worker=_round_total(net*worker_pct/100)
        total=worker
        operator=Decimal(0)
    return {'status':'bounded_reference','month':month,'gross_sgd':money(gross),'transport':transport,
            'feda_pct':str(FEDA[transport]),'cpf_assessable_net_sgd':money(net),'worker_rate_pct':str(worker_pct),
            'operator_rate_pct':str(operator_pct),'worker_share_sgd':money(worker),
            'operator_share_sgd':money(operator),'total_cpf_sgd':money(total),'increased_contribution_pathway':increased,
            'source':SOURCE_PLATFORM_2026,'feda_source':SOURCE_FEDA,'rounding_source':SOURCE_PLATFORM_ROUND,
            'limitations':'One operator, one transport mode, >750 net earnings, 2026 only; actual operating costs are unrelated to FEDA.'}

def self_employed_medisave_2026(*,dob:str,annual_nti,non_pensioner=None,platform_earnings_excluded=None)->dict:
    """2026 non-pensioner SEP annual NTI table (user-confirmed taxable NTI, not gross receipts)."""
    if non_pensioner is not True:return _blocked('Pension status unknown or pensioner; separate rules required',SOURCE_SEP_2026)
    if platform_earnings_excluded is not True:return _blocked('Confirm declared platform net earnings were excluded from SEP NTI',SOURCE_SEP_2026)
    age=age_on(dob,date(2026,1,1));nti=dec(annual_nti,'annual net trade income')
    if nti<0:return _blocked('Negative net trade income not supported')
    if age<45:return _blocked('This narrow implementation serves age 45+; other bands remain research backlog',SOURCE_SEP_2026)
    if nti<=6000:amount=Decimal(0)
    elif age<50:
        if nti<=12000:amount=nti*Decimal('.05')
        elif nti<=18000:amount=Decimal('600')+Decimal('.20')*(nti-Decimal('12000'))
        else:amount=min(nti*Decimal('.10'),Decimal('9600'))
    else:
        if nti<=12000:amount=nti*Decimal('.0525')
        elif nti<=18000:amount=Decimal('630')+Decimal('.21')*(nti-Decimal('12000'))
        else:amount=min(nti*Decimal('.105'),Decimal('10080'))
    return {'status':'bounded_reference','work_year':2026,'age_at_jan1':age,'annual_net_trade_income_sgd':money(nti),
            'annual_medisave_reference_sgd':money(amount),'source':SOURCE_SEP_2026,
            'limitations':'Only age 45+, 2026 non-pensioner, confirmed annual NTI excluding platform earnings; official assessment, payments and tax remain separate.'}

def review_household_contributions(profile:dict)->dict:
    """Inspect eligible income sources; do NOT overwrite any reported financial field."""
    persons={x['id']:x for x in profile['persons']}
    month=profile['as_of'][:7]
    records=[]
    for i in profile.get('income_streams',[]):
        p=persons[i['owner_id']]; kind=i['type']
        if kind=='salary':
            result=employee_ow_cpf(dob=p['dob'],residency=p.get('residency','SG'),month=month,
                                    monthly_ordinary_wages=i['gross_monthly'],pr_cpf_year=p.get('pr_cpf_year'),
                                    additional_wages=i.get('additional_wages'))
        elif kind=='platform':
            result=platform_cpf(dob=p['dob'],month=month,monthly_gross=i['gross_monthly'],
                                transport=i.get('vehicle'),opted_in=i.get('platform_opt_in'),
                                qualifying_platform_worker=i.get('qualifying_platform_worker',True))
        elif kind in ('commission','self_employed','business'):
            if i.get('annual_nti') is None:
                result=_blocked('Annual net trade income explicitly required; not inferred from gross monthly commissions',SOURCE_SEP_2026)
            else:
                result=self_employed_medisave_2026(dob=p['dob'],annual_nti=i['annual_nti'],
                                     non_pensioner=p.get('non_pensioner'),
                                     platform_earnings_excluded=i.get('platform_earnings_excluded'))
        elif kind=='cpf_life':
            result={'status':'user_supplied_only','source':SOURCE_CPF_LIFE,'reason':'CPF LIFE amount requires official payout estimate, no derivation from balances'}
        else:
            continue
        reported=i.get('worker_cpf_monthly')
        if result['status']=='bounded_reference' and reported is not None and 'worker_share_sgd' in result:
            result['reported_worker_cpf_monthly_sgd']=money(reported)
            result['reported_vs_reference_difference_sgd']=money(dec(reported)-dec(result['worker_share_sgd']))
            if dec(reported)!=dec(result['worker_share_sgd']):result['reconciliation']='review_required'
            else:result['reconciliation']='matching_reported_amount'
        records.append({'income_id':i['id'],'income_type':kind,**result})
    return {'version':'SG-bounded-CFP-2026-v1','status':'review_only_not_applied_to_forecast',
            'references':records,'not_calculated':['Income tax','CPF LIFE payout amount','Government benefits eligibility','CPF allocation to OA/SA/RA/MA','2027+ platform-worker rates','2027+ SEP MediSave']}
