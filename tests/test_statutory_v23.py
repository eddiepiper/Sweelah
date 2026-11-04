"""Independent boundary-value oracles from published CPF tables, not fixture-generated expectations."""
import json
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from retirepilot.statutory_2026 import (employee_ow_cpf,platform_cpf,self_employed_medisave_2026,review_household_contributions)
from retirepilot.core import project,validate,ValidationError
from retirepilot.service import evaluate

ROOT=Path(__file__).resolve().parents[1]
def case():return json.loads((ROOT/'data/mixed_income_household.json').read_text())

@pytest.mark.parametrize('dob,year,emp,worker',[
('1980-02-01',2026,'17','20'),('1970-02-01',2026,'16','18'),
('1965-02-01',2026,'12.5','12.5'),('1960-02-01',2026,'9','7.5'),('1955-02-01',2026,'7.5','5'),
('1970-02-01',2027,'16.5','19'),('1965-02-01',2027,'13','13')])
def test_employee_rate_table(dob,year,emp,worker):
    r=employee_ow_cpf(dob=dob,residency='SG',month=f'{year}-11',monthly_ordinary_wages='8000')
    assert (r['employer_rate_pct'],r['worker_rate_pct'])==(emp,worker)
    assert r['status']=='bounded_reference'

def test_cpf_age_transition_is_month_after_55_birthday():
    before=employee_ow_cpf(dob='1971-11-20',residency='SG',month='2026-11',monthly_ordinary_wages='8000')
    after=employee_ow_cpf(dob='1971-11-20',residency='SG',month='2026-12',monthly_ordinary_wages='8000')
    assert before['worker_rate_pct']=='20' and after['worker_rate_pct']=='18'

def test_employee_ordinary_wage_ceiling_and_rounding():
    r=employee_ow_cpf(dob='1970-05-20',residency='SG',month='2026-11',monthly_ordinary_wages='10000')
    assert r['assessable_wages_sgd']=='8000.00'
    assert (r['worker_share_sgd'],r['employer_share_sgd'])==('1440.00','1280.00')
    r=employee_ow_cpf(dob='1971-06-20',residency='SG',month='2027-11',monthly_ordinary_wages='1003.37')
    assert Decimal(r['total_cpf_sgd'])==Decimal('356')
    assert Decimal(r['worker_share_sgd'])==Decimal('190')
    assert Decimal(r['employer_share_sgd'])==Decimal('166')

@pytest.mark.parametrize('params',[
 {'dob':'1970-01-01','residency':'PR','pr_cpf_year':1,'month':'2026-11','monthly_ordinary_wages':'9000'},
 {'dob':'1970-01-01','residency':'SG','month':'2026-11','monthly_ordinary_wages':'750'},
 {'dob':'1970-01-01','residency':'SG','month':'2028-01','monthly_ordinary_wages':'3000'},
 {'dob':'1970-01-01','residency':'SG','month':'2026-11','monthly_ordinary_wages':'3000','additional_wages':'4000'}])
def test_employee_unsupported_cases_do_not_guess(params):
    assert employee_ow_cpf(**params)['status']=='requires_review'

def test_platform_feda_and_non_opted_cpf():
    car=platform_cpf(dob='1974-05-20',month='2026-11',monthly_gross='3000',transport='car',opted_in=False)
    bike=platform_cpf(dob='1977-05-20',month='2026-11',monthly_gross='3000',transport='motorcycle',opted_in=False)
    assert (car['cpf_assessable_net_sgd'],car['worker_share_sgd'])==('1200.00','126.00')
    assert (bike['cpf_assessable_net_sgd'],bike['worker_share_sgd'])==('1950.00','195.00')
    assert car['operator_share_sgd']=='0.00'

def test_platform_opted_worker_has_operator_share():
    x=platform_cpf(dob='1974-05-20',month='2026-11',monthly_gross='3000',transport='car',opted_in=True)
    assert (x['worker_share_sgd'],x['operator_share_sgd'],x['total_cpf_sgd'])==('186.00','84.00','270.00')

def test_platform_unknown_and_2027_block():
    assert platform_cpf(dob='1974-05-20',month='2026-11',monthly_gross='3000',transport='car',opted_in=None)['status']=='requires_review'
    assert platform_cpf(dob='1974-05-20',month='2027-01',monthly_gross='3000',transport='car',opted_in=False)['status']=='requires_review'

def test_2026_self_employed_annual_tiers_not_from_monthly_gross():
    def calc(nti,dob='1974-05-20',**kw):
        return self_employed_medisave_2026(dob=dob,annual_nti=nti,non_pensioner=True,platform_earnings_excluded=True,**kw)
    assert calc('6000')['annual_medisave_reference_sgd']=='0.00'
    assert calc('12000')['annual_medisave_reference_sgd']=='630.00'
    assert calc('15000')['annual_medisave_reference_sgd']=='1260.00'
    assert calc('18000')['annual_medisave_reference_sgd']=='1890.00'
    assert calc('200000')['annual_medisave_reference_sgd']=='10080.00'
    assert calc('15000','1978-05-20')['annual_medisave_reference_sgd']=='1200.00'
    assert self_employed_medisave_2026(dob='1974-05-20',annual_nti='15000',non_pensioner=True,platform_earnings_excluded=None)['status']=='requires_review'

def test_mixed_income_deductions_reconciled_not_auto_replaced():
    p=case();before=evaluate(p,[],1)
    result=before['cpf_contribution_review']
    platform=next(x for x in result['references'] if x['income_id']=='I2')
    assert platform['reconciliation']=='review_required'
    assert platform['reported_vs_reference_difference_sgd']=='74.00'
    assert before['cash_flow']['monthly_surplus']=='700.00'

def test_cpf_housing_requires_explicit_owner_allocations():
    x=case();x['liabilities'][0]['cpf_payment_monthly']='300'
    with pytest.raises(ValidationError,match='explicit owner allocation'):validate(x)
    x['liabilities'][0]['cpf_payment_by_owner_monthly']={'P1':'300'}
    r=project(x,years=1)
    assert Decimal(r['rows'][0]['debt_cpf_payments'])>0
    assert Decimal(r['end_cpf_oa_tracked_no_accrual'])<Decimal('230000')

def test_cpf_housing_owner_depletion_blocks_without_false_cash_shift():
    x=case();x['persons'][0]['cpf_balances']['OA']='100'
    x['liabilities'][0]['cpf_payment_monthly']='300'
    x['liabilities'][0]['cpf_payment_by_owner_monthly']={'P1':'300'}
    with pytest.raises(ValidationError,match='CPF OA balance insufficient'):project(x,years=1)

def test_cpf_housing_allocation_mismatch_and_unknown_balance_rejected():
    x=case();x['liabilities'][0]['cpf_payment_monthly']='300';x['liabilities'][0]['cpf_payment_by_owner_monthly']={'P1':'250'}
    with pytest.raises(ValidationError,match='must equal'):validate(x)
    x['liabilities'][0]['cpf_payment_by_owner_monthly']={'P1':'300'}
    x['persons'][0]['cpf_balances'].pop('OA')
    with pytest.raises(ValidationError,match='OA opening balance unknown'):validate(x)

def test_cpf_life_before_65_invalid_for_1954_plus_birth_cohorts():
    x=case()
    x['income_streams'].append({'id':'CPFL','type':'cpf_life','source':'synthetic_user_provided_estimate','owner_id':'P1','gross_monthly':'1000',
       'starts_age':55,'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'})
    with pytest.raises(ValidationError,match='cannot begin before 65'):validate(x)
