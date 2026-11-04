import json
from copy import deepcopy
from pathlib import Path
from datetime import date
import pytest
from retirepilot.core import validate,monthly_snapshot,project,compare,ValidationError
from retirepilot.adapter import classify_household,build_flat_features
from retirepilot.service import evaluate
from retirepilot.assistant import answer
from retirepilot.policy import policy_reference
from retirepilot.classifier_legacy import make_fixture,evaluate_persona,classify,R,P

ROOT=Path(__file__).resolve().parents[1]
def sample():return json.loads((ROOT/'data/mixed_income_household.json').read_text())
def shocks():return json.loads((ROOT/'data/scenarios.json').read_text())

def test_real_household_cashflow_exact():
    x=monthly_snapshot(sample())
    assert (x['gross_monthly'],x['operating_costs_monthly'],x['tax_cpf_other_deductions_monthly'])==('12000.00','3200.00','1600.00')
    assert (x['net_cash_income_monthly'],x['expenses_monthly'],x['debt_cash_payments_monthly'],x['monthly_surplus'])==('7200.00','4700.00','1800.00','700.00')
    assert x['liquid_assets']=='165000.00'
    assert x['known_net_worth']=='951000.00'
    assert x['essential_cash_runway_months']==27.5

def test_mixed_stream_is_distinct_and_historical():
    x=monthly_snapshot(sample())
    assert len(x['income_streams'])==2
    assert {z['type'] for z in x['income_streams']}=={'commission','platform'}
    assert all(z['history_months']>=6 for z in x['income_streams'])
    assert all(z['gross_income_cv'] is not None for z in x['income_streams'])

def test_every_archetype_considered_with_top_three_only():
    out=classify_household(sample())
    assert out['evaluated']==len(out['all_results'])==96
    assert sum(out['counts'].values())==96
    assert len(out['user_visible_top_three'])<=3
    assert next(x for x in out['all_results'] if x['id']=='B06')['status']!='matched' # No salaried income

def test_archetype_is_deterministic_and_fact_correction_recalculates():
    x=sample(); a=classify_household(x); b=classify_household(deepcopy(x))
    assert a==b
    x['income_streams'][0]['type']='salary';x['income_streams'][0].pop('trade',None)
    c=classify_household(x)
    assert a['counts']!=c['counts'] or a['user_visible_top_three']!=c['user_visible_top_three']

def test_unknown_cpf_opt_in_stays_unknown():
    x=sample();x['income_streams'][1].pop('platform_opt_in')
    out=evaluate(x,[],5)
    assert any('opt-in status unknown' in z for z in out['warnings'])
    assert out['singapore_policy_references']['platform_income_references'][0]['status']=='opt_in_unknown'

def test_missing_cash_assets_blocks_projection_not_assumed_zero():
    x=sample();x.pop('assets')
    d=evaluate(x)
    assert d['cash_flow']['liquid_assets'] is None
    assert d['projection']['status']=='blocked_missing_required_data'

def test_missing_spending_blocks_projection():
    x=sample();x.pop('expenses')
    d=evaluate(x)
    assert d['cash_flow']['monthly_surplus'] is None
    assert d['projection']['status']=='blocked_missing_required_data'

def test_contradictory_reported_field_is_rejected():
    x=sample();x['reported_classification_facts']['person.age_years']=20
    with pytest.raises(ValueError,match='Conflicting'):classify_household(x)

def test_owned_assets_must_sum_to_one():
    x=sample();x['assets'][0]['owners']['P1']='0.8'
    with pytest.raises(ValidationError,match='must total 1'):validate(x)

def test_no_double_count_of_cpf_as_liquid():
    x=sample();s=monthly_snapshot(x)
    assert s['liquid_assets']=='165000.00'
    x['persons'][0]['cpf_balances']['OA']='9999999'
    t=monthly_snapshot(x)
    assert t['liquid_assets']==s['liquid_assets']
    assert t['known_net_worth']!=s['known_net_worth']

def test_invalid_income_deduction_exceeds_gross():
    x=sample();x['income_streams'][0]['operating_costs_monthly']='999999'
    with pytest.raises(ValidationError,match='deductions exceed'):validate(x)

def test_child_education_ends_but_parent_support_remains():
    x=sample(); r=project(x,years=15)['rows']
    assert len(r)==15
    # Schooling expense ends when the named child turns 23; parent's support persists.
    assert int(r[10]['age_end_year'])>int(r[0]['age_end_year'])
    assert all(float(z['spending'])>0 for z in r)

def test_stress_reduces_projected_outcome():
    x=sample();d=compare(x,shocks(),years=15)
    assert float(d['delta_end_accessible_balance'])<0
    assert d['baseline']['rows'][0]['income'] != d['stressed']['rows'][1]['income']
    assert d['stressed']['rows'][2]['market_shock_loss']=='0.00' # shock hits 2027, not 2028

def test_market_shock_does_not_hit_cash_only_portfolio():
    x=sample();x['assets']=[a for a in x['assets'] if a['type']=='cash']
    a=project(x,years=3)
    b=project(x,[{'type':'market_crash','start_year':2027,'duration_years':1,'shock_pct':80}],years=3)
    assert a['end_accessible_balance']==b['end_accessible_balance']

def test_market_shock_only_affects_invested_share_not_property():
    x=sample();d=compare(x,[{'type':'market_crash','start_year':2027,'duration_years':1,'shock_pct':20}],years=3)
    assert float(d['stressed']['rows'][1]['market_shock_loss'])>0
    assert float(d['stressed']['rows'][1]['market_shock_loss'])<100000 # not hitting HDB

def test_cpf_brs_cohort_and_bounded_reference():
    x=sample();x['persons'][0]['dob']='1971-05-20' # 55 in 2026
    r=policy_reference(x)
    checks=r['people'][0]['references']
    assert any(z.get('brs_sgd')==110200 and z.get('frs_sgd')==220400 for z in checks)
    assert all(z['status']!='eligible' for z in checks)

def test_cpf_age_65_70_official_window_not_payout():
    x=sample();x['persons'][0]['dob']='1960-05-20'
    r=policy_reference(x)
    checks=r['people'][0]['references']
    assert any(z['policy']=='CPF-LIFE-PAYOUT-AGE' for z in checks)
    assert all('payout_sgd' not in z for z in checks)

def test_foreign_resident_no_cpf_assumption():
    x=sample();x['persons'][0]['residency']='FOREIGN';x['persons'][0].pop('cpf_balances')
    r=policy_reference(x)
    assert any(z['status']=='requires_review' for z in r['people'][0]['references'])

def test_assistant_gives_grounded_no_product_advice():
    x=sample()
    r=answer(x,'Which stock should I buy?')
    assert r['escalate'] is True
    assert 'cannot recommend specific investments' in r['reply']
    r=answer(x,'How is my monthly cash flow?')
    assert '7200.00' in r['reply']

def test_assistant_references_no_cpf_prediction():
    assert 'cannot derive your CPF LIFE payout' in answer(sample(),'What about CPF payouts?')['reply']

def test_cpf_life_estimate_is_explicit_not_derived():
    x=sample();p=next(i for i in x['income_streams'] if i['id']=='I1')
    x['income_streams'].append({'id':'IL','owner_id':'P1','type':'cpf_life','source':'synthetic_user_provided_estimate','gross_monthly':'1800','starts_age':65,'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'})
    r=project(x,years=15)
    assert any(z['type']=='cpf_life' for z in r['rows'][-1]['income_breakdown'])
    assert all(z['type']!='cpf_life' for z in r['rows'][0]['income_breakdown'])

@pytest.mark.parametrize('pid',sorted(R))
def test_individual_96_legacy_archetype_rule_contract(pid):
    value=evaluate_persona(pid,make_fixture(pid))
    assert value['status']=='matched' and value['evidence_coverage']==100
    assert classify(make_fixture(pid))['evaluated']==96

@pytest.mark.parametrize('pid',sorted(R))
def test_missing_gate_does_not_confirm_archetype(pid):
    assert evaluate_persona(pid,{})['status']=='pending_gate'

@pytest.mark.parametrize('filename',["salaried_household.json","retired_household.json"])
def test_cross_persona_family_samples(filename):
    x=json.loads((ROOT/'data'/filename).read_text())
    report=evaluate(x,[],10)
    assert report['classification']['evaluated']==96
    assert report['projection']['status']=='conditional_estimate'
    assert report['cash_flow']['monthly_surplus'] is not None

def test_spouse_financial_consent_required():
    x=sample();x['persons'][1].pop('consent_for_household_planning')
    with pytest.raises(ValidationError,match='consent required'):validate(x)

def test_protection_covered_person_validation():
    x=sample();x['protection'][0]['covered_person_id']='not_in_household'
    with pytest.raises(ValidationError,match='covered person'):validate(x)

# Experimental LLM adapter is disabled by default and synthetic-only even when enabled.
from retirepilot.llm_adapter import explain_synthetic,ModelDisabledError

def test_external_model_requires_consent():
    with pytest.raises(ModelDisabledError,match='consent'):explain_synthetic(sample(),'Test',False)

def test_external_model_denies_non_synthetic():
    x=sample();x['id']='REAL-PERSON-001'
    with pytest.raises(ModelDisabledError,match='synthetic'):explain_synthetic(x,'Test',True)

def test_external_model_denies_missing_enable_flag(monkeypatch):
    monkeypatch.delenv('RETIREPILOT_EXPERIMENTAL_LLM',raising=False)
    with pytest.raises(ModelDisabledError,match='disabled'):explain_synthetic(sample(),'Test',True)
