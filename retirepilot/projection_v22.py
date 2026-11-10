"""RetirePilot v2.2 monthly cash-flow forecast, synthetic research use only.

No statutory CPF, CPF LIFE, tax, benefits, insurance or investment advice calculations.
Asset investment return and cash yield are separate; debt amortisation uses supplied
interest rates and payments. Retirement is applied to the primary person's earned
income, not to pensions, rentals or expressly approved continuing work.
"""
from __future__ import annotations
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from . import core as _core
from .core import (ValidationError, validate, dec, money, age_on, _scenario_spec, _pct)

EARNED={'salary','platform','commission','self_employed','business'}
REQUIRED_DEDUCTIONS=('cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly')

def incomplete_financial_records(p):
    issues=[]
    for inc in p.get('income_streams',[]):
        for fld in REQUIRED_DEDUCTIONS:
            if fld not in inc or inc[fld] is None:
                issues.append(f"{inc['id']}: missing deduction {fld}")
    for li in p.get('liabilities',[]):
        for fld in ('annual_interest_pct','cash_payment_monthly','cpf_payment_monthly'):
            if fld not in li or li[fld] is None:issues.append(f"{li['id']}: missing liability {fld}")
    return issues

def _anniversary(dob,age):
    """First date on which core.age_on(dob, date) == age (exclusive boundary).

    Must agree with age_on: a 29 Feb birthday is attained on 1 Mar in a common
    year, not 28 Feb, else age-bounded flows start or stop a day early (#9).

    INTERNAL ASSUMPTION (not checked against the CPF Board or any statutory
    convention; Phase 7 external review skipped): the 1 Mar leap-day rule
    follows the engine's existing core.age_on only.

    Delegates to core.attained_age_date. A calendar year outside 1-9999 raises
    core.ValidationError, the error projection_v22 already uses for invalid
    input (mapped to HTTP 422), instead of a raw ValueError/OverflowError.
    """
    return _core.attained_age_date(date.fromisoformat(dob),age,error=ValidationError)

def _overlap_fraction(start,end,begin=None,finish=None):
    a=max([v for v in (start,begin) if v is not None])
    b=min([v for v in (end,finish) if v is not None])
    return Decimal(max((b-a).days,0))/Decimal(monthrange(start.year,start.month)[1])  # full calendar month, not clipped horizon

def _active_fraction_stream(stream,person,start,end,goal):
    begin=_anniversary(person['dob'],int(stream['starts_age'])) if stream.get('starts_age') is not None else None
    finish=_anniversary(person['dob'],int(stream['ends_age'])) if stream.get('ends_age') is not None else None
    if stream['type'] in EARNED and stream['owner_id']==goal.get('primary_id') and not stream.get('continue_after_retirement',False):
        ra=goal.get('retirement_age')
        if ra is not None:
            cutoff=_anniversary(person['dob'],int(ra))
            finish=min(finish,cutoff) if finish is not None else cutoff
    return _overlap_fraction(start,end,begin,finish)

def _active_fraction_expense(exp,persons,start,end):
    if exp.get('end_person_age') is None:return _overlap_fraction(start,end)
    cutoff=_anniversary(persons[exp['person_id']]['dob'],int(exp['end_person_age']))
    return _overlap_fraction(start,end,finish=cutoff)

def _scenario_on(sc,year):
    return sc['start_year']<=year<sc['start_year']+int(sc.get('duration_years',1))

def project_monthly(p,scenarios=None,years=None):
    warnings=validate(p)
    groups=('income_streams','liabilities','expenses','assets')
    missing=[name for name in groups if name not in p]
    if missing:raise ValidationError('projection requires explicit financial groups; unknown not zero: '+', '.join(missing))
    issues=incomplete_financial_records(p)
    if issues:raise ValidationError('projection blocked by incomplete financial records: '+'; '.join(issues))
    asof=date.fromisoformat(p['as_of'])
    persons={r['id']:r for r in p['persons']}
    primary=persons[p['primary_id']]
    initial_age=age_on(primary['dob'],asof)
    goal=p.get('goal',{})
    end_age=int(goal.get('projection_end_age',95))
    if end_age<=initial_age or end_age>110:raise ValidationError('projection_end_age must exceed primary age, at most 110')
    age_horizon_end=_anniversary(primary['dob'],end_age)  # exclusive age-limit boundary
    if years is None:
        n=age_horizon_end.year-asof.year+1
    else:
        if not isinstance(years,int) or years<1:raise ValidationError('projection horizon invalid')
        n=min(years,age_horizon_end.year-asof.year+1)
    if n<1 or n>70:raise ValidationError('projection horizon invalid')
    settings=p.get('assumptions',{})
    inflation=_pct(settings.get('inflation_pct','2.5'))
    invest_r=_pct(settings.get('nominal_return_pct','3.0'))
    cash_r=_pct(settings.get('cash_yield_pct','0'))
    growth=_pct(settings.get('income_growth_pct','0'))
    for key,rate in (('inflation',inflation),('investments',invest_r),('cash',cash_r),('earnings',growth)):
        if rate<=-1:raise ValidationError(key+' annual rate must exceed -100%')
    scenario_list=scenarios or []
    for sc in scenario_list:_scenario_spec(sc)
    # Prevent silent, apparently successful scenarios that target no applicable
    # financial record. These checks are deterministic and are applied before
    # any future cash-flow computation.
    income_by_id={x['id']:x for x in p['income_streams']}
    scenario_income_types={
        'job_loss':EARNED,
        'commission_drop':{'commission','business','self_employed','platform'},
        'rental_vacancy':{'rental'},
        'platform_cost_shock':{'platform'},
    }
    for sc in scenario_list:
        kind=sc['type']
        if sc['start_year']+int(sc.get('duration_years',1))<=asof.year:
            raise ValidationError(f"{kind}: shock period ends before assessment year")
        if kind in scenario_income_types:
            eligible=scenario_income_types[kind]
            ids=sc.get('income_ids')
            if ids:
                unknown=[sid for sid in ids if sid not in income_by_id]
                if unknown:raise ValidationError(f"{kind}: unknown income_ids {unknown}")
                incompatible=[sid for sid in ids if income_by_id[sid]['type'] not in eligible]
                if incompatible:raise ValidationError(f"{kind}: incompatible income types for {incompatible}")
            elif not any(x['type'] in eligible for x in p['income_streams']):
                raise ValidationError(f"{kind}: no applicable income stream exists")
        elif kind=='rent_increase' and not any(e.get('category')=='rent' for e in p['expenses']):
            raise ValidationError('rent_increase: no rent expense supplied')
        elif kind in ('mortgage_rate_shock','housing_payment_shock') and not any(l.get('type')=='mortgage' for l in p['liabilities']):
            raise ValidationError(f'{kind}: no mortgage liability supplied')
    cash=sum((dec(a['value']) for a in p['assets'] if a['type']=='cash' and a.get('accessible',True)),Decimal(0))
    invested=sum((dec(a['value']) for a in p['assets'] if a['type']=='investment' and a.get('accessible',True)),Decimal(0))
    debt_states={l['id']:{'balance':dec(l['balance']),'rate':_pct(l['annual_interest_pct']), 'start_years':l.get('remaining_years'), 'liability':l} for l in p['liabilities']}
    # Deliberately conservative, opening OA balance minus reported housing payments ONLY.
    # Future credited CPF contributions and interest are unknown and excluded.
    cpf_oa={person['id']:dec(person.get('cpf_balances',{}).get('OA','0')) for person in p['persons'] if 'OA' in person.get('cpf_balances',{})}
    startyear=asof.year
    end_calendar_year=startyear+n-1
    monthly=[]
    total_unfunded=Decimal(0)
    first_unfunded=None
    first_term_mismatch=set()
    debt_warnings=[]
    for year in range(startyear,end_calendar_year+1):
        for mon in range(1,13):
            if year==asof.year and mon<asof.month:continue
            daystart=max(1,asof.day) if (year,mon)==(asof.year,asof.month) else 1
            start=date(year,mon,daystart)
            end=date(year+1,1,1) if mon==12 else date(year,mon+1,1)
            if start>=age_horizon_end:continue
            end=min(end,age_horizon_end)
            wholemonth=date(year,mon,1)
            timefraction=Decimal((end-start).days)/Decimal(monthrange(year,mon)[1])  # terminal month is partial
            yoffset=year-startyear
            inflation_factor=(Decimal(1)+inflation)**yoffset
            income_factor=(Decimal(1)+growth)**yoffset
            inflow=Decimal(0)
            breakdown=[]
            for stream in p['income_streams']:
                frac=_active_fraction_stream(stream,persons[stream['owner_id']],start,end,{**goal,'primary_id':p['primary_id']})
                if not frac:continue
                cash_net=dec(stream['gross_monthly'])-sum(dec(stream[k]) for k in REQUIRED_DEDUCTIONS)-dec(stream.get('operating_costs_monthly','0'))
                income=cash_net*frac*(income_factor if stream['type'] in EARNED else Decimal(1))
                original=income
                for sc in scenario_list:
                    if _scenario_on(sc,year) and ((sc['type']=='job_loss' and stream['type'] in EARNED) or (sc['type']=='commission_drop' and stream['type'] in ('commission','business','self_employed','platform')) or (sc['type']=='rental_vacancy' and stream['type']=='rental')):
                        if not sc.get('income_ids') or stream['id'] in sc['income_ids']:
                            income*=Decimal(1)-_pct(sc.get('shock_pct',100))
                for sc in scenario_list:
                    if _scenario_on(sc,year) and sc['type']=='platform_cost_shock' and stream['type']=='platform':
                        if not sc.get('income_ids') or stream['id'] in sc['income_ids']:
                            income-=dec(stream.get('operating_costs_monthly','0'))*frac*_pct(sc['shock_pct'])
                inflow+=income
                breakdown.append({'id':stream['id'],'type':stream['type'],'net_income':money(income),'baseline_before_shock':money(original)})
            spending=Decimal(0)
            for e in p['expenses']:
                expense=dec(e['amount_monthly'])*_active_fraction_expense(e,persons,start,end)*inflation_factor
                if e.get('category')=='rent':
                    for sc in scenario_list:
                        if _scenario_on(sc,year) and sc['type']=='rent_increase':expense*=Decimal(1)+_pct(sc['shock_pct'])
                spending+=expense
            for sc in scenario_list:
                if _scenario_on(sc,year):
                    if sc['type'] in ('care_shock','medical_shock'):spending+=dec(sc['extra_monthly'])*timefraction*inflation_factor
                    if sc['type']=='one_time_cost' and sc['start_year']==year and mon==(asof.month if year==startyear else 1):
                        spending+=dec(sc['extra_once'])*inflation_factor
                    if sc['type']=='inflation_shock':spending*=Decimal(1)+_pct(sc.get('shock_pct',0))
            # Explicit net cash receipt only, not a prediction of inheritance, business sale
            # or entitlement. First eligible modeled month receives once, never repeated.
            for sc in scenario_list:
                if sc['type']=='one_time_windfall' and sc['start_year']==year and mon==(asof.month if year==startyear else 1):
                    inflow+=dec(sc['net_received_once'])
            # Contributions and debt cash schedules are independent of asset returns.
            cash_debt=Decimal(0);cpf_debt=Decimal(0);debt_interest=Decimal(0);principal_paid=Decimal(0)
            for lid,d in debt_states.items():
                bal=d['balance'];li=d['liability']
                if bal<=0:continue
                rate=d['rate']
                for sc in scenario_list:
                    if sc['type']=='mortgage_rate_shock' and li.get('type')=='mortgage' and _scenario_on(sc,year):
                        rate*=Decimal(1)+_pct(sc['shock_pct'])
                interest=bal*rate/Decimal(12)*timefraction
                pcash=dec(li['cash_payment_monthly'])*timefraction
                pcpf=dec(li['cpf_payment_monthly'])*timefraction
                for sc in scenario_list:
                    if sc['type']=='housing_payment_shock' and li.get('type')=='mortgage' and _scenario_on(sc,year):
                        pcash*=Decimal(1)+_pct(sc.get('shock_pct',0))
                pay_total=pcash+pcpf
                actual=min(bal+interest,pay_total)
                if actual<interest: debt_warnings.append(f'{lid}: payment below accrued interest during {year}-{mon:02d}; balance grows')
                cash_paid=actual*(pcash/pay_total) if pay_total else Decimal(0)
                cpf_paid=actual-cash_paid
                if cpf_paid>0:
                    allocation=li.get('cpf_payment_by_owner_monthly',{})
                    if not allocation:raise ValidationError(f'{lid}: CPF ownership allocation missing')
                    for pid,requested in allocation.items():
                        owner_paid=cpf_paid*(dec(requested)/pcpf)
                        if cpf_oa[pid]+Decimal('0.00001')<owner_paid:
                            raise ValidationError(f'{lid}: CPF OA balance insufficient for owner {pid} at {year}-{mon:02d}; future CPF inflows are not modelled')
                        cpf_oa[pid]-=owner_paid
                principal=actual-interest
                d['balance']=bal+interest-actual
                cash_debt+=cash_paid;cpf_debt+=cpf_paid;debt_interest+=interest;principal_paid+=principal
                remaining_years=d['start_years']
                if remaining_years is not None and (year-startyear)*12+mon-asof.month>=int(remaining_years)*12 and d['balance']>Decimal('0.01') and lid not in first_term_mismatch:
                    first_term_mismatch.add(lid)
                    debt_warnings.append(f'{lid}: balance remains after reported remaining term; projection assumes existing payments continue, refinancing or balloon not modelled')
            # A market shock only affects invested balances, never cash.
            market_loss=Decimal(0)
            if mon==(asof.month if year==startyear else 1):
                for sc in scenario_list:
                    if sc['type']=='market_crash' and sc['start_year']==year:
                        loss=invested*_pct(sc.get('shock_pct',0))
                        invested-=loss;market_loss+=loss
            monthly_investment_rate=(Decimal(1)+invest_r)**(Decimal(1)/Decimal(12))-1
            monthly_cash_rate=(Decimal(1)+cash_r)**(Decimal(1)/Decimal(12))-1
            investment_gain=invested*monthly_investment_rate*timefraction
            cash_interest=cash*monthly_cash_rate*timefraction
            invested+=investment_gain;cash+=cash_interest
            net_flow=inflow-spending-cash_debt
            cash+=net_flow
            if cash<0:
                spend_from_investments=min(-cash,invested)
                invested-=spend_from_investments;cash+=spend_from_investments
                if cash<0:
                    total_unfunded+=-cash
                    if first_unfunded is None:first_unfunded=year
                    cash=Decimal(0)
            monthly.append({'month':f'{year}-{mon:02d}','year':year,'age_end_month':age_on(primary['dob'],date(year,mon,monthrange(year,mon)[1])),'fraction':str(timefraction),
                           'income':inflow,'spending':spending,'debt_cash_payments':cash_debt,'debt_cpf_payments':cpf_debt,
                           'debt_interest':debt_interest,'debt_principal':principal_paid,'net_cash_flow':net_flow,
                           'portfolio_gain':investment_gain,'cash_interest':cash_interest,'market_shock_loss':market_loss,
                           'cash_end':cash,'investments_end':invested,'cpf_oa_end':sum(cpf_oa.values(),Decimal(0)),'debt_balance_end':sum((d['balance'] for d in debt_states.values()),Decimal(0)),
                           'unfunded_cumulative':total_unfunded,'income_breakdown':breakdown})
    rows=[]
    for year in range(startyear,end_calendar_year+1):
        seq=[m for m in monthly if m['year']==year]
        if not seq:continue
        def agg(k):return money(sum((m[k] for m in seq),Decimal(0)))
        bystream={}
        for m in seq:
            for b in m['income_breakdown']:
                z=bystream.setdefault(b['id'],{'id':b['id'],'type':b['type'],'net_income_year':Decimal(0),'baseline_before_shock':Decimal(0)})
                z['net_income_year']+=dec(b['net_income']);z['baseline_before_shock']+=dec(b['baseline_before_shock'])
        rows.append({'year':year,'age_end_year':age_on(primary['dob'],age_horizon_end-timedelta(days=1) if age_horizon_end.year==year else date(year,12,31)),
                     'months_modelled':len(seq),'first_year_partial':year==startyear and asof!=date(year,1,1),
                     'income':agg('income'),'spending':agg('spending'),'debt_cash_payments':agg('debt_cash_payments'),
                     'debt_cpf_payments':agg('debt_cpf_payments'),'debt_interest':agg('debt_interest'),'debt_principal':agg('debt_principal'),
                     'net_cash_flow':agg('net_cash_flow'),'portfolio_gain':agg('portfolio_gain'),'cash_interest':agg('cash_interest'),
                     'market_shock_loss':agg('market_shock_loss'),'cash_end':money(seq[-1]['cash_end']),
                     'investments_end':money(seq[-1]['investments_end']),'cpf_oa_end':money(seq[-1]['cpf_oa_end']), 'remaining_debt_end':money(seq[-1]['debt_balance_end']),
                     'accessible_balance_end':money(seq[-1]['cash_end']+seq[-1]['investments_end']),
                     'cumulative_unfunded_cash_need':money(seq[-1]['unfunded_cumulative']),
                     'income_breakdown':[{**z,'net_income_year':money(z['net_income_year']),'baseline_before_shock':money(z['baseline_before_shock'])} for z in sorted(bystream.values(),key=lambda z:z['id'])]})
    warnings+=list(dict.fromkeys(debt_warnings))
    if any(dec(l['cpf_payment_monthly'])>0 for l in p['liabilities']):warnings.append('CPF housing payments deducted from supplied opening OA balances only; no future CPF contributions or interest are modelled, so multiyear forecasts are incomplete')
    warnings.extend(['Cash yield and investment returns are distinct illustrative assumptions, not forecasts',
                     'Retirement target stops primary earned income unless explicit continue_after_retirement is declared',
                     'Projected debt rates/payments are held fixed; refinancing, interest-rate resets and maturity balloon are not fully modelled',
                     'Projected income uses user-reported CPF and tax deductions held constant; 2027 CPF rate changes and later statutory rates are NOT applied automatically; separate bounded CPF review does not change cash flow',
                     'No licensed financial advice or retirement-readiness certification'])
    return {'currency':'SGD','model':'monthly cash-flow prototype v2.4 with 12 bounded scenario operators and no-accrual CPF OA depletion tracking',
            'projection_years':len(rows),'as_of':p['as_of'],
            'assumptions':{'inflation_pct':str(inflation*100),'nominal_return_pct':str(invest_r*100),'cash_yield_pct':str(cash_r*100),
                           'income_growth_pct':str(growth*100)},
            'end_age':end_age,'first_unfunded_year':first_unfunded,'cumulative_unfunded_cash_need':money(total_unfunded),
            'end_accessible_balance':money(cash+invested),'end_cash':money(cash),'end_investments':money(invested),'end_cpf_oa_tracked_no_accrual':money(sum(cpf_oa.values(),Decimal(0))),
            'end_debt_balance':money(sum((d['balance'] for d in debt_states.values()),Decimal(0))),
            'rows':rows,'warnings':warnings}
