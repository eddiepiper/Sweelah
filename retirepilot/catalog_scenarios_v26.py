"""Catalogue contracts, not 46 fully implemented scenarios.

Every original S001-S046 entry has a contract. Limited safe converters are
opt-in and carry disclaimers. No status means production-ready.
"""
from __future__ import annotations
import copy, json
from pathlib import Path
from .core import ValidationError, project, dec, money

REGISTRY_PATH=Path(__file__).resolve().parent.parent/'data/scenario_contracts_v26.json'

def registry():
    return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))

def compile_catalog_scenario(profile:dict, scenario_id:str, params:dict):
    """Compile supported *components* of catalogue scenarios, no entitlement claims.

    The converter never silently translates an unmapped complex event into a
    generic loss. Unsupported scenarios fail closed with their exact blockers.
    """
    index={x['id']:x for x in registry()}
    if scenario_id not in index:raise ValidationError('Unknown scenario catalogue ID')
    contract=index[scenario_id]
    strategy=contract['execution_strategy']
    if strategy=='NOT_SAFE_TO_COMPILE':
        raise ValidationError(f'{scenario_id}: event requires an unimplemented domain-specific model: {contract["blocking_gap"]}')
    if not isinstance(params,dict):raise ValidationError('scenario parameters must be a dict')
    p=copy.deepcopy(profile)
    asof_year=int(p['as_of'][:4]); start=params.get('start_year',asof_year)
    if not isinstance(start,int) or start<asof_year or start>asof_year+50:
        raise ValidationError('start_year must be a future or current supported year')
    duration=params.get('duration_years',1)
    if not isinstance(duration,int) or duration<1 or duration>50:raise ValidationError('duration_years must be 1 to 50')
    events=[]
    if strategy=='RETIREMENT_GOAL_ONLY':
        age=params.get('new_retirement_age')
        if not isinstance(age,int) or age<45 or age>100:raise ValidationError('new_retirement_age is required (45-100)')
        prior=p.get('goal',{}).get('retirement_age')
        if not isinstance(prior,int):raise ValidationError('existing approved retirement age is required')
        if scenario_id=='S005' and age<=prior:raise ValidationError('delayed retirement must increase retirement age')
        if scenario_id=='S029' and age>=prior:raise ValidationError('earlier retirement must reduce retirement age')
        p.setdefault('goal',{})['retirement_age']=age
    elif strategy=='RECURRING_COST_COMPONENT':
        cost=dec(params.get('extra_monthly'))
        if cost<=0:raise ValidationError('positive extra_monthly required')
        events=[{'type':'care_shock','start_year':start,'duration_years':duration,'extra_monthly':str(cost),'shock_pct':0}]
    elif strategy=='NET_CASH_RECEIPT_COMPONENT':
        amount=dec(params.get('net_received_once'))
        if amount<=0:raise ValidationError('positive confirmed net_received_once required')
        events=[{'type':'one_time_windfall','start_year':start,'duration_years':1,'net_received_once':str(amount)}]
    elif strategy=='NET_CASH_GIFT_COMPONENT':
        amount=dec(params.get('net_cash_gift_once'))
        if amount<=0:raise ValidationError('positive net_cash_gift_once required')
        events=[{'type':'one_time_cost','start_year':start,'duration_years':1,'extra_once':str(amount)}]
    else:raise ValidationError('unknown mapping strategy; refuse unsupported behaviour')
    return {'scenario_id':scenario_id,'name':contract['name'],
            'status':'LIMITED_FINANCIAL_COMPONENT_ONLY','strategy':strategy,
            'profile':p,'events':events,'limitations':contract['limitations'],
            'not_an_entitlement_or_regulatory_determination':True}

def compare_catalog_scenario(profile:dict, scenario_id:str, params:dict, *,years:int|None=None):
    c=compile_catalog_scenario(profile,scenario_id,params)
    baseline=project(profile,years=years)
    changed=project(c['profile'],scenarios=c['events'],years=years)
    return {'scenario_id':scenario_id,'status':c['status'],'baseline':baseline,
            'illustration':changed,'delta_end_accessible_balance':money(dec(changed['end_accessible_balance'])-dec(baseline['end_accessible_balance'])),
            'limitations':c['limitations']}
