import json
from pathlib import Path
import pytest
from retirepilot.cpf_retirement_v26 import transition_at_55,cpf_life_official_table_2026,CPFUnsupportedCase
from retirepilot.catalog_scenarios_v26 import registry,compile_catalog_scenario,compare_catalog_scenario
from retirepilot.core import ValidationError, project
ROOT=Path(__file__).resolve().parent.parent
PROFILE=json.loads((ROOT/'data/mixed_income_household.json').read_text())

def test_catalogue_completeness_and_explicit_status():
    rows=registry();assert len(rows)==46
    assert {r['id'] for r in rows}=={f'S{i:03d}' for i in range(1,47)}
    before=[r for r in rows if r['previous_status']=='UNMAPPED']
    assert len(before)==26
    assert sum(r['implemented_component'] for r in before)==7
    assert sum(not r['implemented_component'] for r in before)==19

@pytest.mark.parametrize('sid',[r['id'] for r in registry() if r['execution_strategy']=='NOT_SAFE_TO_COMPILE'])
def test_unimplemented_events_do_not_silently_run(sid):
    with pytest.raises(ValidationError,match='requires an unimplemented'):
        compile_catalog_scenario(PROFILE,sid,{})

@pytest.mark.parametrize('sid,cost',[('S014',200),('S015',500),('S035',700)])
def test_cost_subcomponent_requires_user_value(sid,cost):
    v=compile_catalog_scenario(PROFILE,sid,{'extra_monthly':str(cost),'start_year':2027,'duration_years':2})
    assert v['status']=='LIMITED_FINANCIAL_COMPONENT_ONLY'
    assert v['events'][0]['extra_monthly']==str(cost)
    for bad in (0,-5):
        with pytest.raises(ValidationError):compile_catalog_scenario(PROFILE,sid,{'extra_monthly':bad})

def test_gift_depletes_cash_and_is_not_tax_eligibility():
    v=compile_catalog_scenario(PROFILE,'S044',{'net_cash_gift_once':'1000','start_year':2027})
    assert v['events'][0]['type']=='one_time_cost'
    assert v['not_an_entitlement_or_regulatory_determination'] is True

def test_inheritance_only_user_confirmed_net_cash_receipt():
    c=compile_catalog_scenario(PROFILE,'S042',{'net_received_once':'5000','start_year':2027})
    assert c['events'][0]['type']=='one_time_windfall'
    d=compare_catalog_scenario(PROFILE,'S042',{'net_received_once':'5000','start_year':2027},years=3)
    assert float(d['delta_end_accessible_balance'])>4900
    assert d['status']=='LIMITED_FINANCIAL_COMPONENT_ONLY'
    with pytest.raises(ValidationError):compile_catalog_scenario(PROFILE,'S042',{'net_received_once':'-1'})

def test_retirement_target_recalculated_only_by_explicit_input():
    previous=PROFILE['goal']['retirement_age']
    for sid,age in [('S005',previous+2),('S029',previous-2)]:
        c=compile_catalog_scenario(PROFILE,sid,{'new_retirement_age':age})
        assert c['profile']['goal']['retirement_age']==age
        assert PROFILE['goal']['retirement_age']==previous
    with pytest.raises(ValidationError):compile_catalog_scenario(PROFILE,'S005',{'new_retirement_age':previous-1})

@pytest.mark.parametrize('params',[{}, {'new_retirement_age':102}, {'new_retirement_age':'65'}])
def test_incomplete_retirement_scenario_blocked(params):
    with pytest.raises((ValidationError,ValueError,TypeError)):
        compile_catalog_scenario(PROFILE,'S029',params)

@pytest.mark.parametrize('sid',[f'S{i:03d}' for i in range(1,47)])
def test_all_catalogue_entries_have_limitations(sid):
    c=next(x for x in registry() if x['id']==sid)
    assert c['blocking_gap'] and c['limitations']

def test_ra_transition_sa_then_oa_exact_2026():
    r=transition_at_55(dob='1971-06-01',as_of='2026-06-01',oa='100000',sa='160000',ma='50000',cpf_membership_confirmed=True)
    assert r['frs']=='220400'
    assert r['transfers']['SA_to_RA']=='160000'
    assert r['transfers']['OA_to_RA']=='60400'
    assert r['closing']=={'OA':'39600','SA':'0','MA':'50000','RA':'220400'}
    assert r['below_FRS'] is False

def test_ra_transition_sa_excess_to_oa():
    r=transition_at_55(dob='1972-01-01',as_of='2027-01-01',oa='1000',sa='250000',ma='20000',cpf_membership_confirmed=True)
    assert r['frs']=='228200'
    assert r['transfers']['SA_to_OA_excess']=='21800'
    assert r['closing']['OA']=='22800'

def test_ra_transition_below_frs_not_automatic_rejection():
    r=transition_at_55(dob='1971-10-13',as_of='2026-10-13',oa='10000',sa='15000',ma='0',cpf_membership_confirmed=True)
    assert r['closing']['RA']=='25000' and r['below_FRS'] is True

@pytest.mark.parametrize('kw',[
    {'dob':'1970-05-01','as_of':'2025-05-01','oa':'100','sa':'200','ma':'300','cpf_membership_confirmed':True},
    {'dob':'1971-05-01','as_of':'2026-05-02','oa':'100','sa':'200','ma':'300','cpf_membership_confirmed':True},
    {'dob':'1971-05-01','as_of':'2026-05-01','oa':'100','sa':'200','ma':'300'},
    {'dob':'1971-05-01','as_of':'2026-05-01','oa':'100','sa':'200','ma':'300','existing_ra':'5','cpf_membership_confirmed':True},
    {'dob':'1971-05-01','as_of':'2026-05-01','oa':'100','sa':'200','ma':'300','cpf_membership_confirmed':True,'property_pledge':True},
    {'dob':'1971-05-01','as_of':'2026-05-01','oa':'nan','sa':'200','ma':'300','cpf_membership_confirmed':True},
])
def test_ra_transition_fail_closed(kw):
    with pytest.raises(CPFUnsupportedCase):transition_at_55(**kw)

@pytest.mark.parametrize('ra,age,expected',[
    (50000,65,490),(110200,65,950),(220400,65,1780),(440800,70,4580),
])
def test_exact_published_life_reference_no_interpolation(ra,age,expected):
    r=cpf_life_official_table_2026(ra_age55=ra,payout_start_age=age)
    assert r['illustrative_monthly_SGD']==str(expected)
    assert r['status']=='published_illustration_not_personal_estimate'

@pytest.mark.parametrize('kw',[{'ra_age55':200000,'payout_start_age':65},
    {'ra_age55':220400,'payout_start_age':66},
    {'ra_age55':220400,'payout_start_age':65,'plan':'Escalating'}])
def test_no_personal_life_or_interpolated_payout(kw):
    with pytest.raises(CPFUnsupportedCase):cpf_life_official_table_2026(**kw)
