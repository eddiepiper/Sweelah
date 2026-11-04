"""Prior failing requirements, now enforced as normal passing tests on RetirePilot v2.2.
No xfail markers; a failure blocks acceptance.
Run: cd /mnt/data && python -m pytest -r x -q test_retirepilot_unmet_acceptance_2026_11_03.py
"""
import sys,json
from copy import deepcopy
from pathlib import Path
import pytest
# Current package imported from the remediation project root
# No external source imports permitted
from retirepilot.core import project
from retirepilot.service import evaluate
from retirepilot.classifier_legacy import R,P,evaluate_persona,make_fixture,classify
ROOT=Path(__file__).resolve().parents[1]
def sample():return json.loads((ROOT/'data/mixed_income_household.json').read_text())

def test_retirement_age_changes_cashflow():
    x=sample();y=deepcopy(x);x['goal']['retirement_age']=55;y['goal']['retirement_age']=65
    assert project(x,years=15)['rows']!=project(y,years=15)['rows']

def test_missing_deductions_block_or_flag_incomplete_calculation():
    x=sample()
    for s in x['income_streams']:
        for k in ('cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):
            s.pop(k,None)
    result=evaluate(x,[],1)
    assert result['projection']['status']=='blocked_missing_required_data' or any('missing deduction' in w.lower() for w in result['cash_flow']['warnings'])

def test_cash_yield_separate_from_investment_return():
    x=sample();x['assets']=[a for a in x['assets'] if a['type']=='cash']
    y=deepcopy(x);x['assumptions']['nominal_return_pct']='3';y['assumptions']['nominal_return_pct']='20'
    assert project(x,years=1)['rows'][0]['portfolio_gain']==project(y,years=1)['rows'][0]['portfolio_gain']

def test_partial_first_calendar_year_is_prorated():
    x=sample();r=project(x,years=1)['rows'][0]
    assert r['year']==2026 and float(r['income']) < 86400

def test_zero_point_match_is_not_user_visible():
    r=R['A01'];profile=make_fixture('A01',positive=False)
    for c in r['criteria']:
        pred=P[c['predicate']];op=pred['op'];v=pred['expected']
        if op=='EQ':wrong=not(v=='true') if v in ('true','false') else 'different'
        elif op=='HAS':wrong=['different']
        elif op=='IN':wrong='different'
        elif op=='GTE':wrong=float(v)-1
        elif op=='GT':wrong=float(v)
        elif op=='LTE':wrong=float(v)+1
        elif op=='LT':wrong=float(v)
        else:raise AssertionError(op)
        profile[pred['field']]=wrong
    match=evaluate_persona('A01',profile)
    assert match['observed_score']==0 and match['evidence_coverage']==100
    assert match['status']!='matched' and 'A01' not in [x['id'] for x in classify(profile)['user_visible_top_three']]