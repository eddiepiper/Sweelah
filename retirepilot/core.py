"""Deterministic, local-only financial analysis for RetirePilot demonstration.

No user data is persisted. No automatic tax calculation, statutory CPF deductions,
CPF interest accrual, insurance claims, or eligibility decisions are performed.
All deductions and CPF LIFE estimates must be supplied explicitly by the user.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import date
from copy import deepcopy
from math import isfinite
from statistics import pstdev
from typing import Any

CENT = Decimal('0.01')
ALLOWED_INCOME = {'salary','platform','commission','self_employed','business','rental','pension','cpf_life','investment','other'}
ALLOWED_ASSET = {'cash','investment','property','business','other'}
ALLOWED_SCENARIO = {'job_loss','commission_drop','care_shock','inflation_shock','market_crash','housing_payment_shock',
                    'medical_shock','rent_increase','rental_vacancy','platform_cost_shock','one_time_cost','one_time_windfall','mortgage_rate_shock'}

class ValidationError(ValueError):
    pass

def dec(v: Any, label: str = 'value') -> Decimal:
    if isinstance(v, bool):
        raise ValidationError(f'{label}: boolean is not an amount')
    try:
        d = Decimal(str(v))
        if not d.is_finite(): raise ValidationError(f'{label}: finite number required')
        return d
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(f'{label}: decimal amount expected')

def money(v: Any) -> str:
    return str(dec(v).quantize(CENT, rounding=ROUND_HALF_UP))

def age_on(dob: str, on: date) -> int:
    born = date.fromisoformat(dob)
    return on.year - born.year - ((on.month,on.day) < (born.month,born.day))

def _id_set(rows, group):
    ids=[r['id'] for r in rows]
    if len(set(ids)) != len(ids): raise ValidationError(f'{group}: duplicate id')
    return set(ids)

def _positive_amount(row, fld, label, allow_negative=False):
    if fld in row and row[fld] is not None:
        v=dec(row[fld], f'{label}.{fld}')
        if v < 0 and not allow_negative:raise ValidationError(f'{label}.{fld}: negative amount forbidden')
        return v
    return None

def validate(profile: dict) -> list[str]:
    """Validate structural invariants, preserve unknown values as None.

    All list fields are optional for progressive onboarding; omitted is unknown,
    not evidence that no financial item exists.
    """
    if not isinstance(profile,dict):raise ValidationError('household must be object')
    if profile.get('currency','SGD')!='SGD':raise ValidationError('SGD-only prototype')
    try: asof=date.fromisoformat(profile['as_of'])
    except (KeyError,ValueError,TypeError):raise ValidationError('as_of requires ISO date')
    members=profile.get('persons',[])
    if not isinstance(members,list) or not members:raise ValidationError('at least one person required')
    persons=_id_set(members,'persons')
    for p in members:
        if p.get('role') not in ('primary','spouse','child','parent','dependent','other'):raise ValidationError('person role invalid')
        if p.get('role') not in ('primary','child') and p.get('cpf_balances') and p.get('consent_for_household_planning') is not True:
            raise ValidationError(f'{p["id"]}: explicit adult consent required for CPF details')
        try: born=date.fromisoformat(p['dob'])
        except (KeyError,ValueError,TypeError):raise ValidationError('person DOB invalid')
        if born>asof: raise ValidationError('date of birth in future')
        if p.get('residency','SG') not in ('SG','PR','FOREIGN'):raise ValidationError('residency invalid')
        for acct,balance in p.get('cpf_balances',{}).items():
            if acct not in ('OA','SA','MA','RA'):raise ValidationError('unexpected CPF account')
            _positive_amount({'amount':balance},'amount',f'{p["id"]}.cpf')
    if profile.get('primary_id') not in persons:raise ValidationError('primary_id must identify person')
    for group in ('income_streams','assets','liabilities','expenses','relationships','protection'):
        if group in profile and not isinstance(profile[group],list):raise ValidationError(f'{group}: list required')
        _id_set(profile.get(group,[]),group)
    for inc in profile.get('income_streams',[]):
        if inc.get('owner_id') not in persons:raise ValidationError(f'income {inc["id"]}: unknown owner')
        if inc.get('type') not in ALLOWED_INCOME:raise ValidationError('unknown income type')
        if inc.get('gross_monthly') is None:
            raise ValidationError(f"{inc['id']}: gross_monthly required for a reported income stream; missing is unknown")
        if inc.get('type')=='cpf_life':
            # A published CPF LIFE example is not a member-specific estimate.
            # The synthetic fixture exception never authorises real customer data.
            source=inc.get('source')
            allowed={'member_transcribed_official_cpf_estimate'}
            if str(profile.get('id','')).startswith('RP-SYNTH-'):
                allowed.add('synthetic_user_provided_estimate')
            if source not in allowed:
                raise ValidationError(f"{inc['id']}: member-provided official CPF LIFE estimate source required; published tables are not personalised payouts")
            holder=next(x for x in members if x['id']==inc['owner_id'])
            if date.fromisoformat(holder['dob']).year>=1954:
                reported_start=int(inc['starts_age']) if inc.get('starts_age') is not None else None
                if reported_start is not None and reported_start<65:
                    raise ValidationError(f"{inc['id']}: CPF LIFE payouts cannot begin before 65 for a member born in 1954 or later")
                if reported_start is None and age_on(holder['dob'],asof)<65:
                    raise ValidationError(f"{inc['id']}: CPF LIFE start age required for a member currently below 65")
        if inc.get('type') in ('platform','commission','self_employed','business','rental') and inc.get('operating_costs_monthly') is None:
            # Do not equate unknown business/rental operating costs to zero.
            raise ValidationError(f"{inc['id']}: operating_costs_monthly required (explicit 0 permitted)")
        for f in ('gross_monthly','operating_costs_monthly','cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):
            _positive_amount(inc,f,inc['id'])
        gross=dec(inc.get('gross_monthly','0'))
        out=sum((dec(inc.get(f,'0')) for f in ('operating_costs_monthly','cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly')),Decimal(0))
        if out>gross:raise ValidationError(f'{inc["id"]}: deductions exceed receipts')
        hist=inc.get('history',[])
        if not isinstance(hist,list):raise ValidationError('income history must be list')
        months=[]
        for h in hist:
            if len(str(h.get('month',''))) != 7: raise ValidationError('history month requires YYYY-MM')
            try: date.fromisoformat(h['month']+'-01')
            except ValueError:raise ValidationError('history month invalid')
            months.append(h['month'])
            _positive_amount(h,'gross',inc['id']+'.history')
            _positive_amount(h,'operating_costs',inc['id']+'.history')
        if len(set(months)) != len(months):raise ValidationError('duplicate income observation month')
        if inc.get('platform_opt_in') not in (None,True,False):raise ValidationError('platform_opt_in must be boolean or unknown')
    for item in profile.get('assets',[]):
        if item.get('type') not in ALLOWED_ASSET:raise ValidationError('asset type invalid')
        if item.get('value') is None:
            raise ValidationError(f"{item['id']}: asset value unknown; provide a documented estimate or omit the asset and mark the financial assessment incomplete")
        _positive_amount(item,'value',item['id'])
        _validate_ownership(item,persons)
    for item in profile.get('liabilities',[]):
        for f in ('balance','cash_payment_monthly','cpf_payment_monthly','annual_interest_pct'):
            _positive_amount(item,f,item['id'])
        if item.get('balance') is None:
            raise ValidationError(f"{item['id']}: liability balance unknown; cannot assume zero")
        _validate_ownership(item,persons)
        cpf_due=dec(item.get('cpf_payment_monthly','0')) if item.get('cpf_payment_monthly') is not None else Decimal(0)
        if cpf_due>0:
            allocation=item.get('cpf_payment_by_owner_monthly')
            if not isinstance(allocation,dict) or not allocation:
                raise ValidationError(f"{item['id']}: CPF-funded repayments require explicit owner allocation")
            allocated=Decimal(0)
            for owner,amount in allocation.items():
                if owner not in item['owners'] or owner not in persons:
                    raise ValidationError(f"{item['id']}: CPF payment owner must have a stated ownership share")
                value=dec(amount,'CPF owner allocation')
                if value<0:raise ValidationError('CPF owner allocation cannot be negative')
                holder=next(p for p in members if p['id']==owner)
                if 'OA' not in holder.get('cpf_balances',{}):
                    raise ValidationError(f"{item['id']}: {owner} OA opening balance unknown; CPF housing forecast blocked")
                allocated+=value
            if allocated!=cpf_due:
                raise ValidationError(f"{item['id']}: CPF owner allocations must equal CPF monthly payment")
        if item.get('remaining_years') is not None and int(item['remaining_years'])<0:raise ValidationError('remaining_years negative')
    for item in profile.get('expenses',[]):
        _positive_amount(item,'amount_monthly',item['id'])
        if item.get('person_id') is not None and item['person_id'] not in persons:raise ValidationError('expense person missing')
        if item.get('end_person_age') is not None and item.get('person_id') is None:raise ValidationError('age-based expense requires person_id')
    for coverage in profile.get('protection',[]):
        if coverage.get('covered_person_id') not in persons:raise ValidationError('protection covered person missing')
        for f in ('premium_monthly','insured_benefit'):_positive_amount(coverage,f,coverage['id'])
    # Household membership is not consent to access another adult's financial records.
    asof_ages={p['id']:age_on(p['dob'],asof) for p in members}
    for person in members:
        pid=person['id']
        if pid==profile['primary_id'] or asof_ages[pid]<18:continue
        references=bool(person.get('cpf_balances')) or any(x.get('owner_id')==pid for x in profile.get('income_streams',[]))
        references=references or any(pid in x.get('owners',{}) for group in ('assets','liabilities') for x in profile.get(group,[]))
        references=references or any(x.get('person_id')==pid for x in profile.get('expenses',[]))
        references=references or any(x.get('covered_person_id')==pid for x in profile.get('protection',[]))
        if references and person.get('consent_for_household_planning') is not True:
            raise ValidationError(f'{pid}: explicit adult consent required for referenced financial records')
    for r in profile.get('relationships',[]): 
        if r.get('from_id') not in persons:raise ValidationError('relationship from_id missing')
        if r.get('to_id') and r.get('to_id') not in persons:raise ValidationError('relationship to_id missing; use external_description for non-members')
    goal=profile.get('goal',{})
    if goal:
        retirement=int(goal.get('retirement_age',65))
        if retirement<45 or retirement>100:raise ValidationError('retirement_age out of bound')
    assumptions=profile.get('assumptions',{})
    for k in ('inflation_pct','nominal_return_pct','income_growth_pct','cash_yield_pct'):
        if k in assumptions and not -50<=dec(assumptions[k])<=100:raise ValidationError('assumption outside supported range')
    warnings=[]
    for required_group in ('income_streams','liabilities'):
        if required_group not in profile:
            warnings.append(f'{required_group} not supplied; unknown must not be treated as zero')
    if age_on(next(p['dob'] for p in members if p['id']==profile['primary_id']),asof)<45: warnings.append('Below primary age-45 target; extension pathway only')
    if any(p.get('residency')=='FOREIGN' for p in members):warnings.append('Foreign resident: no automatic CPF eligibility assumption')
    if not profile.get('assets'):warnings.append('Assets not supplied; net worth and investable runway cannot be confirmed')
    if not profile.get('expenses'):warnings.append('Expenses not supplied; surplus and runway cannot be confirmed')
    if not any(p.get('cpf_balances') for p in members):warnings.append('CPF account balances missing; CPF position cannot be assessed')
    warnings.append('Unless explicitly sourced otherwise, amounts are synthetic or user-reported, not independently verified')
    if not any(i['type']=='cpf_life' for i in profile.get('income_streams',[])):warnings.append('No CPF LIFE payout estimate; no payout inferred from CPF balances')
    from .projection_v22 import incomplete_financial_records
    warnings.extend(incomplete_financial_records(profile))
    for i in profile.get('income_streams',[]):
        if i['type'] in ('platform','commission','self_employed') and len(i.get('history',[]))<6:warnings.append(f'{i["id"]}: fewer than 6 months of observed income; volatility not established')
        if i['type']=='platform' and i.get('platform_opt_in') is None:warnings.append(f'{i["id"]}: platform CPF opt-in status unknown; no statutory contribution estimate')
    if any(dec(l.get('cpf_payment_monthly','0'))>0 for l in profile.get('liabilities',[])):
        warnings.append('CPF-funded debt repayments are recorded but future CPF account depletion is not projected')
    return warnings

def _validate_ownership(item,persons):
    shares=item.get('owners')
    if not isinstance(shares,dict) or not shares:raise ValidationError(f'{item["id"]}: owner shares required')
    total=Decimal(0)
    for k,v in shares.items():
        if k not in persons:raise ValidationError('unknown asset/liability owner')
        share=dec(v,'ownership share')
        if share<0 or share>1:raise ValidationError('ownership share out of bounds')
        total+=share
    if total!=1:raise ValidationError(f'{item["id"]}: ownership shares must total 1, got {total}')

def _income_net(i):
    return dec(i.get('gross_monthly','0'))-sum((dec(i.get(k,'0')) for k in ('operating_costs_monthly','cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly')),Decimal(0))

def _active_income(i,ages: dict[str,int]):
    age=ages[i['owner_id']]
    return (i.get('starts_age') is None or age>=int(i['starts_age'])) and (i.get('ends_age') is None or age<int(i['ends_age']))

def _active_expense(e,ages):
    if e.get('end_person_age') is not None:
        return ages[e['person_id']]<int(e['end_person_age'])
    return True

def monthly_snapshot(p:dict) -> dict:
    warnings=validate(p)
    asof=date.fromisoformat(p['as_of'])
    ages={x['id']:age_on(x['dob'],asof) for x in p['persons']}
    active=[i for i in p.get('income_streams',[]) if _active_income(i,ages)]
    gross=sum((dec(x.get('gross_monthly','0')) for x in active),Decimal(0))
    operating=sum((dec(x.get('operating_costs_monthly','0')) for x in active),Decimal(0))
    deduction=sum((dec(x.get('cash_deductions_monthly','0'))+dec(x.get('worker_cpf_monthly','0'))+dec(x.get('tax_reserve_monthly','0')) for x in active),Decimal(0))
    from .projection_v22 import incomplete_financial_records
    missing_cash=any('missing deduction' in x for x in incomplete_financial_records(p))
    cash_income=None if missing_cash else gross-operating-deduction
    expenses=sum((dec(e.get('amount_monthly','0')) for e in p.get('expenses',[]) if _active_expense(e,ages)),Decimal(0))
    essential=sum((dec(e.get('amount_monthly','0')) for e in p.get('expenses',[]) if e.get('essential',False) and _active_expense(e,ages)),Decimal(0))
    debt=sum((dec(l.get('cash_payment_monthly','0')) for l in p.get('liabilities',[])),Decimal(0))
    available=None if not p.get('expenses') or 'income_streams' not in p or 'liabilities' not in p or cash_income is None else cash_income-expenses-debt
    liquid=sum((dec(x['value']) for x in p.get('assets',[]) if x['type'] in ('cash','investment') and x.get('accessible',True)),Decimal(0))
    assets=sum((dec(x['value']) for x in p.get('assets',[])),Decimal(0))
    cpf_known=sum((sum((dec(v) for v in x.get('cpf_balances',{}).values()),Decimal(0)) for x in p['persons']),Decimal(0))
    debt_bal=sum((dec(x.get('balance','0')) for x in p.get('liabilities',[])),Decimal(0))
    networth=(assets+cpf_known-debt_bal) if (p.get('assets') and p.get('liabilities') is not None and all('value' in x for x in p['assets'])) else None
    total_essential=essential+debt
    runway=round(float(liquid/total_essential),1) if total_essential>0 and p.get('assets') and p.get('expenses') and 'liabilities' in p else None
    streams=[]
    for i in p.get('income_streams',[]):
        hist=[float(dec(h['gross'])) for h in i.get('history',[]) if 'gross' in h]
        v=round(pstdev(hist)/(sum(hist)/len(hist)),4) if len(hist)>=3 and sum(hist)>0 else None
        streams.append({'id':i['id'],'type':i['type'],'active':_active_income(i,ages),'monthly_net_cash':money(_income_net(i)) if not any(k not in i or i[k] is None for k in ('cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly')) else None,'history_months':len(hist),'gross_income_cv':v,'cpf_regime':'User-reported cash deductions only; no statutory amount calculated'})
    return {'as_of':p['as_of'],'currency':'SGD','gross_monthly':money(gross) if 'income_streams' in p else None, 'operating_costs_monthly':money(operating) if 'income_streams' in p else None,'tax_cpf_other_deductions_monthly':money(deduction) if not missing_cash and 'income_streams' in p else None,
            'net_cash_income_monthly':money(cash_income) if cash_income is not None and 'income_streams' in p else None,'expenses_monthly':money(expenses) if p.get('expenses') else None,
            'essential_expenses_monthly':money(essential) if p.get('expenses') else None,
            'debt_cash_payments_monthly':money(debt) if 'liabilities' in p else None,'monthly_surplus':money(available) if available is not None else None,
            'liquid_assets':money(liquid) if p.get('assets') else None,'all_assets_reported':money(assets) if p.get('assets') else None,
            'cpf_balances_reported':money(cpf_known) if any(x.get('cpf_balances') for x in p['persons']) else None,
            'liabilities_reported':money(debt_bal) if 'liabilities' in p else None,
            'known_net_worth':money(networth) if networth is not None else None,
            'essential_cash_runway_months':runway,'income_streams':streams,'warnings':warnings}

def _pct(x):return dec(x)/100

def _scenario_spec(s):
    if s.get('type') not in ALLOWED_SCENARIO:raise ValidationError('unsupported scenario type')
    if not isinstance(s.get('start_year'),int):raise ValidationError('scenario start_year must be int')
    duration=int(s.get('duration_years',1))
    if duration<1 or duration>50:raise ValidationError('duration_years outside limits')
    shock=dec(s.get('shock_pct','0'))
    if shock<0 or shock>100:raise ValidationError('shock_pct must be between 0 and 100')
    if s['type'] in ('care_shock','medical_shock'):
        if s.get('extra_monthly') is None or dec(s['extra_monthly'])<0:
            raise ValidationError(f"{s['type']}.extra_monthly must be explicitly provided and nonnegative")
    if s['type']=='one_time_cost' and (s.get('extra_once') is None or dec(s['extra_once'])<0):
        raise ValidationError('one_time_cost.extra_once must be provided and nonnegative')
    if s['type']=='one_time_windfall' and (s.get('net_received_once') is None or dec(s['net_received_once'])<0):
        raise ValidationError('one_time_windfall.net_received_once must be provided and nonnegative')
    if s.get('income_ids') is not None:
        if not isinstance(s['income_ids'],list) or any(not isinstance(v,str) for v in s['income_ids']):
            raise ValidationError('scenario income_ids must be an array of identifiers')
    return duration,shock

def project(p:dict, scenarios:list[dict]|None=None, years:int|None=None) -> dict:
    """Calendar-period monthly projection, aggregated to year rows (v2.2)."""
    from .projection_v22 import project_monthly
    return project_monthly(p,scenarios=scenarios,years=years)

def compare(p:dict, scenarios:list[dict], years:int|None=None):
    b=project(p,years=years);s=project(p,scenarios,years=years)
    return {'baseline':b,'stressed':s,'delta_end_accessible_balance':money(dec(s['end_accessible_balance'])-dec(b['end_accessible_balance'])),
            'delta_cumulative_unfunded_need':money(dec(s['cumulative_unfunded_cash_need'])-dec(b['cumulative_unfunded_cash_need']))}
