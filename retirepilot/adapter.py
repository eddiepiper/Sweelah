"""Versioned, conservative bridge from canonical household records to the 96-rule legacy taxonomy.
Unobserved attributes remain absent. Manual facts are never accepted as policy eligibility.
"""
from __future__ import annotations
from datetime import date
from statistics import pstdev
from decimal import Decimal
from .core import dec,age_on,monthly_snapshot
from .classifier_legacy import classify,P

TRUTHY={'true':True,'false':False}
ALLOWED_MANUAL_FIELDS={p['field'] for p in P.values()}  # Prototype only; explicit user-reported labels


def build_flat_features(h:dict) -> dict:
    snap=monthly_snapshot(h)
    person=next(p for p in h['persons'] if p['id']==h['primary_id'])
    asof=date.fromisoformat(h['as_of'])
    age=age_on(person['dob'],asof)
    f={'person.age_years':age,'person.citizenship':'sg' if person.get('residency')=='SG' else 'other','person.residency':'pr' if person.get('residency')=='PR' else ('sg' if person.get('residency')=='SG' else 'foreign')}
    if 'pass_type' in person:f['person.pass_type']=person['pass_type']
    if 'marital_status' in person:f['relationships.marital_status']=person['marital_status']
    if 'employment_status' in person:f['employment.retirement_status']=person['employment_status']
    if h.get('goal',{}).get('retirement_age') is not None:
        ra=int(h['goal']['retirement_age']);f.update({'goals.target_retirement_age':ra,'goals.retirement_target_set':True,'goals.years_to_retirement':max(0,ra-age),'goals.pre65_income_bridge_needed':ra<65})
    if h.get('goal',{}).get('retirement_country'):f['goals.retirement_country']=h['goal']['retirement_country']
    incs=h.get('income_streams',[])
    if 'income_streams' in h:
        t=sorted(set(i['type'] for i in incs))
        cls=set()
        if 'salary' in t:cls.add('employee')
        if any(z in t for z in ('commission','self_employed','business')):cls.add('self_employed')
        if 'platform' in t:cls.add('platform')
        f.update({'income_stream.type':t,'income_stream.type_count':len(t),'income_stream.worker_class':sorted(cls),
                  'income_stream.platform_secondary':('platform' in t and len(t)>1),
                  'person.has_earned_income':any(i['type'] in ('salary','commission','platform','self_employed','business') and dec(i.get('gross_monthly','0'))>0 for i in incs),
                  'income_stream.actual_business_expenses':str(sum((dec(i.get('operating_costs_monthly','0')) for i in incs if i['type'] in ('commission','platform','self_employed','business')),Decimal(0))),
                  'household.earners_count':len({i['owner_id'] for i in incs if i['type'] in ('salary','commission','platform','self_employed','business') and dec(i.get('gross_monthly','0'))>0})})
        gross_for_primary=sum((dec(i.get('gross_monthly','0'))*12 for i in incs if i['owner_id']==h['primary_id']),Decimal(0))
        gross_hh=sum((dec(i.get('gross_monthly','0'))*12 for i in incs),Decimal(0))
        def band(v):return 'low' if v<100000 else 'middle' if v<200000 else 'high'
        f.update({'income.annual_personal_band':band(gross_for_primary),'household.annual_income_band':band(gross_hh)})
        pf=[i for i in incs if i['type']=='platform']
        if pf:
            if all(i.get('platform_opt_in') is not None for i in pf):
                f['cpf.platform_opt_in_state']='opted_in' if any(i['platform_opt_in'] for i in pf) else 'not_opted_in'
                f['cpf.platform_medisave_only']=not any(i['platform_opt_in'] for i in pf)
            if any(i.get('platform_service') for i in pf):f['income_stream.platform_type']=next(i['platform_service'] for i in pf if i.get('platform_service'))
            if any(i.get('vehicle') for i in pf):f['income_stream.platform_vehicle']=next(i['vehicle'] for i in pf if i.get('vehicle'))
            f['income_stream.active_platforms']=len({i.get('payer',i['id']) for i in pf})
            f['income_stream.distinct_platform_payers']=len({i.get('payer',i['id']) for i in pf})
            f['income_stream.vehicle_costs_reported']=any(dec(i.get('operating_costs_monthly','0'))>0 for i in pf)
            f['cpf.platform_contribution_exists']=any(dec(i.get('worker_cpf_monthly','0'))>0 for i in pf)
        if 'salary' in t and 'platform' in t:f['cpf.multiple_contribution_pathways']=True
        if any(dec(i.get('worker_cpf_monthly','0'))>0 for i in incs):f['cpf.contribution_recent']=True
        c=[i for i in incs if i['type']=='commission']
        if c:
            f['income_stream.commission_history_months']=max(len(i.get('history',[])) for i in c)
            if any(i.get('trade') for i in c):f['income_stream.trade']=next(i['trade'] for i in c if i.get('trade'))
        histories=[float(dec(x['gross'])) for i in incs for x in i.get('history',[]) if 'gross' in x]
        if len(histories)>=6 and sum(histories)>0:
            f['income_stream.volatility_state']='variable' if pstdev(histories)/(sum(histories)/len(histories))>=0.25 else 'stable'
    if 'persons' in h:f['household.members_count']=len(h['persons'])
    if 'relationships' in h:
        rel=h['relationships'];children=[x for x in rel if x.get('kind')=='child'];parents=[x for x in rel if x.get('kind')=='parent']
        f.update({'relationships.children_count':len(children),'relationships.dependent_children_count':sum(x.get('financially_dependent',False) for x in children),
                  'relationships.parents_supported_count':sum(x.get('financially_dependent',False) for x in parents),
                  'relationships.adult_children_count':sum(x.get('adult_child',False) for x in children),
                  'relationships.adult_children_supported':sum(x.get('adult_child',False) and x.get('financially_dependent',False) for x in children),
                  'household.children_resident_count':sum(x.get('to_id') is not None for x in children),
                  'household.generations_count':3 if any(x.get('to_id') for x in parents) and children else 2 if children or parents else 1})
    partners=[p for p in h['persons'] if p.get('role')=='spouse']
    if partners and 'income_streams' in h:
        partner_ids={p['id'] for p in partners};f['relationships.partner_has_income']=any(i['owner_id'] in partner_ids and dec(i.get('gross_monthly','0'))>0 for i in incs)
    if 'assets' in h:
        assets=h['assets'];liquid=sum((dec(a['value']) for a in assets if a['type'] in ('cash','investment') and a.get('accessible',True)),Decimal(0))
        prop=[a for a in assets if a['type']=='property']
        f.update({'assets.liquid_band':'low' if liquid<100000 else ('high' if liquid>=500000 else 'mid'), 'assets.liquid_assets_exist':liquid>0,
                  'assets.investment_exists':any(a['type']=='investment' for a in assets),
                  'assets.property_count':len(prop),'assets.residential_property_count':len(prop),'assets.overseas_exists':any(a.get('country','SG')!='SG' for a in assets),
                  'assets.overseas_property_exists':any(a.get('country','SG')!='SG' for a in prop), 'assets.business_equity_exists':any(a['type']=='business' for a in assets)})
        if prop:
            f['housing.property_type']='hdb_owner' if prop[0].get('subtype')=='hdb' else ('private_condo_owner' if prop[0].get('subtype')=='condo' else 'other')
            f['assets.property_share_material']=sum(dec(a['value']) for a in prop)*2>sum((dec(a['value']) for a in assets),Decimal(0))
            f['housing.lease_details_complete']=all(a.get('remaining_lease_years') is not None for a in prop)
            f['housing.tenure']='owner'
        elif any(e.get('category')=='rent' for e in h.get('expenses',[])):
            f['housing.tenure']='renting'
    if 'liabilities' in h:
        liab=h['liabilities'];mort=[x for x in liab if x.get('type')=='mortgage' and dec(x.get('balance','0'))>0]
        f.update({'liabilities.active_mortgage':bool(mort),'liabilities.housing_loan_balance':str(sum((dec(x.get('balance','0')) for x in mort),Decimal(0))),
                 'liabilities.monthly_mortgage_payment':str(sum((dec(x.get('cash_payment_monthly','0')) for x in mort),Decimal(0))),
                 'liabilities.nonhousing_loan_exists':any(x.get('type')!='mortgage' and dec(x.get('balance','0'))>0 for x in liab)})
    if 'expenses' in h:
        totals={}
        for e in h['expenses']:
            totals[e.get('category','other')]=totals.get(e.get('category','other'),Decimal(0))+dec(e.get('amount_monthly','0'))*12
        mapping={'education':'expenses.children_education','parent_support':'expenses.family_transfers','care':'expenses.care_annual','medical':'expenses.medical_annual','rent':'expenses.property_rental_costs'}
        for k,v in mapping.items():f[v]=str(totals.get(k,0))
        if snap['expenses_monthly'] is not None and snap['net_cash_income_monthly'] is not None and dec(snap['net_cash_income_monthly'])>0:
            f['expenses.essential_income_ratio']='high' if dec(snap['essential_expenses_monthly'])/dec(snap['net_cash_income_monthly'])>=Decimal('0.7') else 'normal'
    if snap.get('monthly_surplus') is not None:f['financials.projected_surplus']=snap['monthly_surplus']
    if snap.get('net_cash_income_monthly') is not None and 'liabilities' in h and dec(snap['net_cash_income_monthly'])>0:
        f['financials.debt_service_burden']='high' if dec(snap['debt_cash_payments_monthly'])/dec(snap['net_cash_income_monthly'])>Decimal('0.4') else 'normal'
    if 'cpf_balances' in person:
        f['cpf.is_member']=True
        f['cpf.ra_balance_known']='RA' in person['cpf_balances']
    # Manually reported attributes must be explicit and cannot overwrite derived fields.
    for field,value in h.get('reported_classification_facts',{}).items():
        if field not in ALLOWED_MANUAL_FIELDS:raise ValueError(f'Unrecognized classification field {field}')
        if field in f and f[field]!=value:raise ValueError(f'Conflicting reported and derived field {field}')
        f[field]=value
    return f


def classify_household(h:dict) -> dict:
    flat=build_flat_features(h)
    out=classify(flat)
    out['derived_field_count']=len(flat)
    out['taxonomy_coverage_fields']=177
    out['unknown_field_count']=177-len(flat)
    out['methodology']=['Canonical household values + explicitly reported facts; unspecified attributes remain unknown',
                        'Proposed thresholds and scores are uncalibrated; top three are NOT financial priority rankings']
    return out
