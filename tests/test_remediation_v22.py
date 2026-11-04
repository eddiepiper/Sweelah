"""Independent specification-oriented regression cases for known Phase 2-5 defects.
Oracles are calendar arithmetic and explicit requirements, not generated persona fixtures.
Tests describe technical, synthetic behaviour only, not regulatory financial correctness.
"""
import json
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from retirepilot.core import monthly_snapshot,project,compare,ValidationError
from retirepilot.service import evaluate
from retirepilot.adapter import classify_household
from retirepilot.classifier_legacy import classify,evaluate_persona,make_fixture,R,P

ROOT=Path(__file__).resolve().parents[1]
def sample(name='mixed_income_household.json'):
    return json.loads((ROOT/'data'/name).read_text())

def low_score_profile(pid):
    r=R[pid];record=make_fixture(pid,positive=False)
    for c in r['criteria']:
        spec=P[c['predicate']];op=spec['op'];v=spec['expected']
        if op=='EQ':wrong=not(v=='true') if v in ('true','false') else '__no_match__'
        elif op=='IN':wrong='__no_match__'
        elif op=='HAS':wrong=['__no_match__']
        elif op=='GTE':wrong=Decimal(v)-1
        elif op=='GT':wrong=Decimal(v)
        elif op=='LTE':wrong=Decimal(v)+1
        elif op=='LT':wrong=Decimal(v)
        else:raise AssertionError(op)
        record[spec['field']]=wrong
    return record

@pytest.mark.parametrize('pid',sorted(R))
def test_all_96_retain_id_and_do_not_show_zero_matches(pid):
    o=evaluate_persona(pid,low_score_profile(pid))
    if o['gate'] is True and o['exclusion'] is False and o['observed_score']==0:
        assert o['status']=='not_relevant'
        assert pid not in [x['id'] for x in classify(low_score_profile(pid))['user_visible_top_three']]

def test_no_zero_score_in_top_three_on_mixed_household():
    r=classify_household(sample());assert r['evaluated']==96
    assert all(x['observed_score']>=60 for x in r['user_visible_top_three'])
    assert sum(r['counts'].values())==96

def test_persona_matching_deterministic_96_results():
    x=sample();a=classify_household(x);b=classify_household(deepcopy(x))
    assert a==b and len(a['all_results'])==96

def test_financial_snapshot_reference_unchanged():
    r=monthly_snapshot(sample())
    assert (r['gross_monthly'],r['net_cash_income_monthly'],r['monthly_surplus'])==('12000.00','7200.00','700.00')

def test_missing_deductions_block_and_not_zero():
    x=sample()
    for s in x['income_streams']:
        for k in ('cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):s.pop(k,None)
    s=monthly_snapshot(x);r=evaluate(x,[],3)
    assert s['net_cash_income_monthly'] is None and s['monthly_surplus'] is None
    assert r['projection']['status']=='blocked_missing_required_data'
    assert any('missing deduction' in v for v in r['projection']['required'])
    with pytest.raises(ValidationError,match='incomplete financial records'):project(x,years=1)

def test_missing_mortgage_rate_blocks_projection():
    x=sample();x['liabilities'][0].pop('annual_interest_pct')
    assert evaluate(x)['projection']['status']=='blocked_missing_required_data'
    with pytest.raises(ValidationError,match='missing liability annual_interest_pct'):project(x,years=1)

def test_user_entered_zero_still_distinct_from_unknown():
    x=sample();x['income_streams'][1]['cash_deductions_monthly']='0'
    assert monthly_snapshot(x)['monthly_surplus']=='700.00'

def test_retirement_age_changes_trajectory():
    x=sample();y=deepcopy(x)
    x['goal']['retirement_age']=55;y['goal']['retirement_age']=65
    a=project(x,years=6)['rows'];b=project(y,years=6)['rows']
    assert a[0]['income']==b[0]['income']
    assert Decimal(a[3]['income'])<Decimal(b[3]['income'])
    assert Decimal(a[4]['income'])==0
    assert Decimal(b[4]['income'])>0
    assert a != b

def test_explicit_continued_work_can_override_retirement_cesstion():
    x=sample();x['goal']['retirement_age']=55
    a=project(x,years=6)
    x['income_streams'][0]['continue_after_retirement']=True
    b=project(x,years=6)
    assert Decimal(b['rows'][4]['income'])>Decimal(a['rows'][4]['income'])

def test_pension_not_stopped_by_earned_income_retirement():
    x=sample();x['goal']['retirement_age']=55
    x['income_streams'].append({'id':'CPFL','type':'cpf_life','source':'synthetic_user_provided_estimate','owner_id':'P1','gross_monthly':'1000','starts_age':65,'cash_deductions_monthly':'0','tax_reserve_monthly':'0','worker_cpf_monthly':'0'})
    a=project(x,years=16)['rows'];assert a[4]['income']=='0.00';assert Decimal(a[-1]['income'])>0

def test_partial_first_year_2026():
    x=sample();r=project(x,years=1)['rows'][0]
    assert r['year']==2026 and r['first_year_partial'] is True
    # 28 days including Nov 3 of 30-day November, plus December.
    frac=Decimal(28)/Decimal(30)+1
    assert Decimal(r['income'])==Decimal('7200')*frac
    assert abs(Decimal(r['spending'])-Decimal('4700')*frac)<Decimal('0.01')
    assert abs(Decimal(r['debt_cash_payments'])-Decimal('1800')*frac)<Decimal('0.01')
    assert abs(Decimal(r['net_cash_flow'])-Decimal('700')*frac)<Decimal('0.01')

def test_cash_and_investment_returns_distinct():
    x=sample();x['assets']=[a for a in x['assets'] if a['type']=='cash']
    y=deepcopy(x)
    x['assumptions']['nominal_return_pct']='3';y['assumptions']['nominal_return_pct']='20'
    a=project(x,years=1)['rows'][0];b=project(y,years=1)['rows'][0]
    assert a['portfolio_gain']==b['portfolio_gain']=='0.00'
    assert a['cash_interest']==b['cash_interest']=='0.00'
    x['assumptions']['cash_yield_pct']='4'
    assert Decimal(project(x,years=1)['rows'][0]['cash_interest'])>0

def test_market_shock_only_reduces_investment_not_cash():
    x=sample();base=project(x,years=2);s=project(x,[{'type':'market_crash','start_year':2027,'shock_pct':40,'duration_years':1}],years=2)
    assert Decimal(s['rows'][1]['market_shock_loss'])>0
    assert Decimal(s['end_investments'])<Decimal(base['end_investments'])

@pytest.mark.parametrize('pct',[-100,-1,101])
def test_invalid_scenario_shock_rejected(pct):
    x=sample()
    with pytest.raises(ValidationError):project(x,[{'type':'job_loss','start_year':2027,'duration_years':1,'shock_pct':pct}],years=2)

def test_debt_amortizes_without_automatic_writeoff():
    x=sample();x['as_of']='2026-01-01'
    x['liabilities']=[{'id':'LOAN','type':'mortgage','balance':'12000','annual_interest_pct':'0','cash_payment_monthly':'1200','cpf_payment_monthly':'0','remaining_years':1,'owners':{'P1':'1'}}]
    r=project(x,years=1)['rows'][0]
    assert r['debt_cash_payments']=='12000.00'
    assert r['remaining_debt_end']=='0.00'
    assert r['debt_interest']=='0.00'

def test_debt_interest_accrues_and_open_balance_decreases():
    x=sample();x['as_of']='2026-01-01'
    x['liabilities']=[{'id':'LOAN','type':'mortgage','balance':'1200','annual_interest_pct':'12','cash_payment_monthly':'110','cpf_payment_monthly':'0','remaining_years':1,'owners':{'P1':'1'}}]
    r=project(x,years=1)['rows'][0]
    assert Decimal(r['debt_interest'])>0
    assert Decimal(r['remaining_debt_end'])<Decimal('1200')
    assert Decimal(r['debt_cash_payments'])<=Decimal('1320')

def test_cpf_debt_payment_not_double_counted_as_cash():
    x=sample();x['liabilities'][0]['cpf_payment_monthly']='300'
    x['liabilities'][0]['cpf_payment_by_owner_monthly']={'P1':'300'}
    r=project(x,years=1)['rows'][0]
    assert Decimal(r['debt_cpf_payments'])>0
    assert Decimal(r['debt_cash_payments'])==Decimal('3480')
    assert any('CPF housing payments deducted' in w for w in project(x,years=1)['warnings'])
    assert Decimal(r['cpf_oa_end'])<Decimal('160000')+Decimal('70000')

def test_unsupported_scenario_explicitly_rejected():
    x=sample()
    with pytest.raises(ValidationError,match='unsupported scenario type'):
        project(x,[{'type':'business_sale','start_year':2027}],years=2)

def test_default_projection_reaches_goal_end_age_not_a_year_short():
    x=sample();x['goal']['projection_end_age']=95
    p=project(x)
    last=p['rows'][-1]
    assert last['year']==2069
    assert last['age_end_year']==94   # Stop before 95th birthday in May 2069
    assert last['months_modelled']==5

def test_retirement_income_starts_from_legal_payout_age_not_calendar_january():
    x=sample();x['income_streams'].append({'id':'CPFL','type':'cpf_life','source':'synthetic_user_provided_estimate','owner_id':'P1',
       'gross_monthly':'1000','starts_age':65,'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'})
    x['goal']['retirement_age']=55
    r=project(x,years=16)['rows']
    # P1 turns 65 on 20 May 2039. The first payout year is partial.
    assert r[13]['year']==2039
    assert Decimal(r[13]['income'])>0
    assert Decimal(r[13]['income'])<Decimal('12000')
    assert Decimal(r[14]['income'])==Decimal('12000')
