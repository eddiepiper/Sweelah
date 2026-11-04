"""Phase 7 challenge tests written outside the self-generated archetype fixtures.
Golden values are specified independently as expected accounting outcomes.
"""
import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import pytest
from retirepilot.core import monthly_snapshot, project, validate, ValidationError
from retirepilot.policy import policy_reference
from retirepilot.service import evaluate
from retirepilot.adapter import classify_household

ROOT=Path(__file__).resolve().parents[1]
def case():return json.loads((ROOT/'data/mixed_income_household.json').read_text())

def adjusted(case_name):
    x=case()
    if case_name=='baseline': pass
    elif case_name=='without_platform':x['income_streams']=[x['income_streams'][0]]
    elif case_name=='commission_lower':x['income_streams'][0]['gross_monthly']='7200'
    elif case_name=='extra_salary':x['income_streams'].append({'id':'I3','owner_id':'P1','type':'salary','gross_monthly':'4000','worker_cpf_monthly':'800','cash_deductions_monthly':'0','tax_reserve_monthly':'0'})
    elif case_name=='additional_care':x['expenses'].append({'id':'E99','category':'care','amount_monthly':'1200','essential':True})
    elif case_name=='higher_mortgage_cash':x['liabilities'][0]['cash_payment_monthly']='2500'
    elif case_name=='higher_tax_reserve':x['income_streams'][1]['tax_reserve_monthly']='1100'
    elif case_name=='no_mortgage_cash':x['liabilities'][0]['cash_payment_monthly']='0'
    elif case_name=='no_commission_operating_cost':x['income_streams'][0]['operating_costs_monthly']='0'
    elif case_name=='two_extra_children_costs':x['expenses'].append({'id':'E98','category':'education','amount_monthly':'600','essential':True})
    return x

@pytest.mark.parametrize('name,net,expense,debt,surplus',[
 ('baseline','7200','4700','1800','700'),
 ('without_platform','5700','4700','1800','-800'),
 ('commission_lower','5400','4700','1800','-1100'),
 ('extra_salary','10400','4700','1800','3900'),
 ('additional_care','7200','5900','1800','-500'),
 ('higher_mortgage_cash','7200','4700','2500','0'),
 ('higher_tax_reserve','6200','4700','1800','-300'),
 ('no_mortgage_cash','7200','4700','0','2500'),
 ('no_commission_operating_cost','9200','4700','1800','2700'),
 ('two_extra_children_costs','7200','5300','1800','100')
])
def test_independent_monthly_golden_cases(name,net,expense,debt,surplus):
    r=monthly_snapshot(adjusted(name))
    assert tuple(Decimal(r[k]) for k in ('net_cash_income_monthly','expenses_monthly','debt_cash_payments_monthly','monthly_surplus'))==tuple(map(Decimal,(net,expense,debt,surplus)))

def test_independent_one_year_nominal_reference():
    r=project(case(),years=1)['rows'][0]
    assert r['net_cash_flow']=='1353.33'  # 28/30 of November plus full December
    assert r['portfolio_gain']=='429.64'  # Investment-only prorated monthly compounding
    assert r['accessible_balance_end']=='166782.98'

def test_independent_care_shock_difference():
    r=project(case(),[{'type':'care_shock','start_year':2026,'duration_years':1,'extra_monthly':'1200'}],years=1)['rows'][0]
    assert r['spending']=='11406.67'  # Baseline 9086.67 plus 1200*(28/30+1)
    assert r['accessible_balance_end']=='164462.98'

@pytest.mark.parametrize('damage,expected',[
 (lambda x:x['assets'][0].pop('value'),'asset value unknown'),
 (lambda x:x['income_streams'][0].pop('gross_monthly'),'gross_monthly required'),
 (lambda x:x['income_streams'][0].pop('operating_costs_monthly'),'operating_costs_monthly required'),
 (lambda x:x['liabilities'][0].pop('balance'),'liability balance unknown'),
])
def test_missing_structured_financial_data_never_zero(damage,expected):
    x=case();damage(x)
    with pytest.raises(ValidationError,match=expected):validate(x)

def test_spouse_income_requires_consent_even_without_cpf():
    x=case();x['persons'][1].pop('cpf_balances');x['persons'][1].pop('consent_for_household_planning')
    x['income_streams'].append({'id':'SPI','type':'salary','owner_id':'P2','gross_monthly':'1000'})
    with pytest.raises(ValidationError,match='explicit adult consent'):validate(x)

def test_spouse_ownership_requires_consent_even_without_cpf():
    x=case();x['persons'][1].pop('cpf_balances');x['persons'][1].pop('consent_for_household_planning')
    with pytest.raises(ValidationError,match='explicit adult consent'):validate(x)

def test_unobserved_spouse_dob_without_financial_records_allowed():
    x=case();x['persons'][1].pop('cpf_balances');x['persons'][1].pop('consent_for_household_planning')
    for z in x['assets']+x['liabilities']:
        if 'P2' in z['owners']:
            z['owners'].pop('P2');z['owners']['P1']='1'
    assert validate(x)

def test_reject_negative_care_expense_injection():
    with pytest.raises(ValidationError,match='care_shock.extra_monthly'):
        project(case(),[{'type':'care_shock','start_year':2026,'duration_years':1,'extra_monthly':'-50000'}],years=1)

def test_reject_missing_care_expense_magnitude():
    with pytest.raises(ValidationError,match='care_shock.extra_monthly'):
        project(case(),[{'type':'care_shock','start_year':2026,'duration_years':1}],years=1)

def test_reject_invalid_income_id_type():
    with pytest.raises(ValidationError,match='scenario income_ids'):
        project(case(),[{'type':'job_loss','start_year':2026,'duration_years':1,'income_ids':'I1'}],years=1)

def test_pr_contribution_not_inferred_when_pr_year_unknown():
    x=case();x['persons'][0]['residency']='PR';x['persons'][0].pop('pr_cpf_year',None)
    r=policy_reference(x)['people'][0]['references']
    assert any(x['status']=='requires_review' for x in r)
    assert not any(x.get('employee_pct') for x in r)

def test_pr_standard_reference_only_after_explicit_third_year_status():
    x=case();x['persons'][0]['residency']='PR';x['persons'][0]['pr_cpf_year']=3
    r=policy_reference(x)['people'][0]['references']
    assert any(x.get('employee_pct')==20 for x in r)

def test_multi_persona_simultaneous_reproducibility():
    p=case(); a=classify_household(p); b=classify_household(deepcopy(p))
    assert a==b and a['evaluated']==96 and len(a['all_results'])==96

def test_no_statutory_calculation_claims():
    r=evaluate(case(),[],1)
    assert r['singapore_policy_references']['status']=='reference_only_not_eligibility'
    assert r['projection']['status']=='conditional_estimate'

@pytest.mark.parametrize('dob,expected_employer,expected_worker',[
 ('1971-11-03',17,20),    # exactly 55 in 2026
 ('1969-11-03',16,18),    # 57
 ('1964-11-03',12.5,12.5), # 62
 ('1959-11-03',9,7.5),   # 67
 ('1951-11-03',7.5,5),   # 75
])
def test_2026_employee_reference_age_rates_official_aggregate_only(dob,expected_employer,expected_worker):
    x=case();x['persons'][0]['dob']=dob
    refs=policy_reference(x)['people'][0]['references']
    y=next(z for z in refs if z['policy']=='CPF-EMP-2026')
    assert y['employer_pct']==expected_employer
    assert y['employee_pct']==expected_worker
    assert y['status']=='reference_only'

def test_2027_employee_rates_not_backcast_as_2026():
    x=case();x['as_of']='2027-01-15'
    refs=policy_reference(x)['people'][0]['references']
    assert not any(z['policy']=='CPF-EMP-2026' and z.get('employee_pct') for z in refs)

def test_missing_income_group_blocks_without_zero_report():
    x=case();x.pop('income_streams')
    a=evaluate(x,[],1)
    assert a['projection']['status']=='blocked_missing_required_data'
    assert a['cash_flow']['net_cash_income_monthly'] is None

def test_missing_liabilities_group_blocks_without_zero_report():
    x=case();x.pop('liabilities')
    a=evaluate(x,[],1)
    assert a['projection']['status']=='blocked_missing_required_data'
    assert a['cash_flow']['debt_cash_payments_monthly'] is None

def test_projection_direct_call_refuses_incomplete_financial_groups():
    x=case();x.pop('liabilities')
    with pytest.raises(ValidationError,match='projection requires explicit financial groups'):
        project(x,years=1)


def test_export_button_does_not_claim_anonymity():
    html=(ROOT/'retirepilot/ui.html').read_text()
    assert 'Export anonymised' not in html
    assert 'review before sharing' in html
