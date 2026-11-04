import json,os,tempfile
from pathlib import Path
from copy import deepcopy
from cryptography.fernet import Fernet
import pytest
from retirepilot.financial_references_v24 import (resident_tax_reference,static_cpf_interest_reference,housing_sale_reference)
from retirepilot.local_vault_v24 import LocalVault,VaultError
from retirepilot.planner_session_v24 import guided_reply,next_question
from retirepilot.classifier_legacy import classify
from retirepilot.core import ValidationError

BASE=Path(__file__).resolve().parent.parent

def sample():return json.loads((BASE/'data/mixed_income_household.json').read_text())

@pytest.mark.parametrize('chargeable,expected',[
    ('0','0.00'),('20000','0.00'),('30000','200.00'),('40000','550.00'),
    ('80000','3350.00'),('120000','7950.00'),('160000','13950.00'),
    ('200000','21150.00'),('240000','28750.00'),('280000','36550.00'),
    ('320000','44550.00'),('500000','84150.00'),('1000000','199150.00'),('1100000','223150.00')])
def test_tax_official_brackets(chargeable,expected):
    r=resident_tax_reference(chargeable_income=chargeable,year_of_assessment=2026,resident_confirmed=True,chargeable_income_confirmed=True)
    assert r['status']=='bounded_reference' and r['tax_before_rebates_sgd']==expected

def test_tax_blocks_false_gross_income_substitution():
    r=resident_tax_reference(chargeable_income='120000',year_of_assessment=2026,resident_confirmed=True,chargeable_income_confirmed=False)
    assert r['status']=='requires_review'

def test_tax_blocks_future_year_and_nonresidents():
    for kw in [dict(year_of_assessment=2028,resident_confirmed=True),dict(year_of_assessment=2026,resident_confirmed=False)]:
        r=resident_tax_reference(chargeable_income='50000',chargeable_income_confirmed=True,**kw)
        assert r['status']=='requires_review'

def test_cpf_simple_rate_case():
    r=static_cpf_interest_reference(age=50,balances={'OA':'50000','SA':'10000'},as_of_quarter='2026Q4',no_transactions_confirmed=True)
    assert r['status']=='illustrative_static_balance_reference'
    assert r['base_interest_annualised_sgd']=='1650.00'
    assert r['extra_interest_annualised_sgd']=='300.00'

def test_cpf_55_extra_interest_priority():
    r=static_cpf_interest_reference(age=60,balances={'OA':'30000','RA':'30000'},as_of_quarter='2026Q4',no_transactions_confirmed=True)
    assert r['extra_interest_annualised_sgd']=='800.00'

def test_cpf_55_with_sa_blocked():
    r=static_cpf_interest_reference(age=60,balances={'SA':'25000'},as_of_quarter='2026Q4',no_transactions_confirmed=True)
    assert r['status']=='requires_review'

def test_cpf_future_rate_unverified():
    assert static_cpf_interest_reference(age=50,balances={'OA':'5000'},as_of_quarter='2027Q4',no_transactions_confirmed=True)['status']=='requires_review'

def test_housing_sale_waterfall():
    r=housing_sale_reference(sale_price=800000,outstanding_loan=200000,required_cpf_refund=150000,sale_costs=20000,property_rule_class='hdb',official_refund_confirmed=True)
    assert r['cash_sale_proceeds_sgd']=='430000.00'

def test_housing_sale_unknown_refund_fails_closed():
    r=housing_sale_reference(sale_price=800000,outstanding_loan=200000,required_cpf_refund=150000,sale_costs=20000,property_rule_class='hdb',official_refund_confirmed=False)
    assert r['status']=='requires_review'

def test_housing_sale_loan_more_than_proceeds_fails_closed():
    r=housing_sale_reference(sale_price=200000,outstanding_loan=250000,required_cpf_refund=1000,sale_costs=1000,property_rule_class='hdb',official_refund_confirmed=True)
    assert r['status']=='requires_review'

def setup_vault(tmp_path):
    return LocalVault(tmp_path/'vault'/'records.sqlite',key=Fernet.generate_key())

def test_vault_requires_encryption_key(tmp_path,monkeypatch):
    monkeypatch.delenv('RETIREPILOT_VAULT_KEY',raising=False)
    with pytest.raises(VaultError,match='required'):LocalVault(tmp_path/'x.sqlite')

def test_vault_requires_all_adult_consent_and_encrypts(tmp_path):
    p=sample();v=setup_vault(tmp_path)
    try:
        with pytest.raises(VaultError,match='Independent'):v.put_profile(p)
        v.grant_consent(p['id'],'P1','household_planning',explicit=True)
        with pytest.raises(VaultError,match='Independent'):v.put_profile(p)
        v.grant_consent(p['id'],'P2','household_planning',explicit=True)
        v.put_profile(p)
        assert v.get_profile(p['id'])==p
        assert b'1974-05-20' not in (tmp_path/'vault'/'records.sqlite').read_bytes()
        assert ((tmp_path/'vault'/'records.sqlite').stat().st_mode & 0o077)==0
    finally:v.close()

def test_vault_revocation_deletes_financial_profile(tmp_path):
    p=sample();v=setup_vault(tmp_path)
    try:
        for pid in ('P1','P2'):v.grant_consent(p['id'],pid,'household_planning',explicit=True)
        v.put_profile(p);v.revoke_consent(p['id'],'P2','household_planning')
        with pytest.raises(VaultError):v.get_profile(p['id'])
    finally:v.close()

def test_vault_memory_and_action_require_purpose_consent(tmp_path):
    p=sample();v=setup_vault(tmp_path)
    try:
        for pid in ('P1','P2'):v.grant_consent(p['id'],pid,'household_planning',explicit=True)
        v.put_profile(p)
        with pytest.raises(VaultError):v.save_memory(p['id'],'P1','M1','Retirement goal age 65')
        v.grant_consent(p['id'],'P1','local_memory',explicit=True)
        v.save_memory(p['id'],'P1','M1','Retirement goal age 65')
        assert v.list_memory(p['id'],'P1')[0]['evidence']=='user_reported_unverified'
        with pytest.raises(VaultError):v.create_action(p['id'],'P1','A1','Check CPF','Retrieve official balances')
        v.grant_consent(p['id'],'P1','action_tracking',explicit=True)
        v.create_action(p['id'],'P1','A1','Check CPF','Retrieve official balances')
        with pytest.raises(VaultError):v.transition_action(p['id'],'A1','approved',actor='user')
        v.transition_action(p['id'],'A1','approved',actor='user',approval=True)
        v.transition_action(p['id'],'A1','in_progress',actor='user')
        v.transition_action(p['id'],'A1','reported_complete',actor='user')
        with pytest.raises(VaultError):v.transition_action(p['id'],'A1','verified',actor='user',evidence_ref='fake',verifier='user')
        result=v.transition_action(p['id'],'A1','simulated_verified',actor='user',evidence_ref='synthetic-official-receipt',verifier='second-reviewer')
        assert result['verified_complete'] is False
        assert result['simulation']['simulation_only'] is True
    finally:v.close()

def test_vault_rejects_real_user_profiles(tmp_path):
    p=sample();p['id']='REAL-USER-123';v=setup_vault(tmp_path)
    try:
        with pytest.raises(VaultError):v.put_profile(p)
    finally:v.close()

def test_assistant_is_not_action_engine():
    p=sample();r=guided_reply(p,'What should I do next?')
    assert r['financial_actions_executed'] is False
    assert r['requires_user_review'] is True
    assert 'next_question' in r

def test_assistant_progressive_question_missing_group():
    p=sample();del p['assets']
    assert next_question(p)['field']=='assets'

from retirepilot.core import project,compare

def stress(profile,scenario):
    return compare(profile,[scenario],years=3)

def test_new_medical_cost_changes_cash_and_not_income():
    p=sample();r=stress(p,{'type':'medical_shock','start_year':2027,'duration_years':1,'extra_monthly':'500'})
    assert float(r['delta_end_accessible_balance'])<0
    row_b=next(x for x in r['baseline']['rows'] if x['year']==2027)
    row_s=next(x for x in r['stressed']['rows'] if x['year']==2027)
    assert round(float(row_s['spending'])-float(row_b['spending']),2)==6150
    assert row_s['income']==row_b['income']

def test_rent_increase_only_rent_expense():
    p=sample();p['expenses'].append({'id':'E-RENT','category':'rent','amount_monthly':'1000','essential':True})
    r=stress(p,{'type':'rent_increase','start_year':2027,'duration_years':1,'shock_pct':20})
    b=next(x for x in r['baseline']['rows'] if x['year']==2027)
    s=next(x for x in r['stressed']['rows'] if x['year']==2027)
    assert round(float(s['spending'])-float(b['spending']),2)==205.0*12  # 2.5% inflation on S$200 delta

def test_rental_vacancy_does_not_change_salary():
    p=sample();p['income_streams'].append({'id':'I-RENT','owner_id':'P1','type':'rental','gross_monthly':'1200','operating_costs_monthly':'100',
                      'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'200'})
    r=stress(p,{'type':'rental_vacancy','start_year':2027,'duration_years':1,'shock_pct':100,'income_ids':['I-RENT']})
    b=next(x for x in r['baseline']['rows'] if x['year']==2027)
    s=next(x for x in r['stressed']['rows'] if x['year']==2027)
    assert round(float(b['income'])-float(s['income']),2)==900*12

def test_platform_cost_shock_reduces_income():
    p=sample();r=stress(p,{'type':'platform_cost_shock','start_year':2027,'duration_years':1,'shock_pct':50,'income_ids':['I2']})
    b=next(x for x in r['baseline']['rows'] if x['year']==2027)
    s=next(x for x in r['stressed']['rows'] if x['year']==2027)
    assert float(b['income'])>float(s['income'])

def test_one_time_cost_occurs_once():
    p=sample();r=stress(p,{'type':'one_time_cost','start_year':2027,'duration_years':2,'extra_once':'1000'})
    for year in (2027,2028):
        b=next(x for x in r['baseline']['rows'] if x['year']==year)
        s=next(x for x in r['stressed']['rows'] if x['year']==year)
        if year==2027:assert round(float(s['spending'])-float(b['spending']),2)==1025
        else:assert s['spending']==b['spending']

def test_mortgage_rate_shock_affects_debt_not_fixed_payment():
    p=sample();r=stress(p,{'type':'mortgage_rate_shock','start_year':2027,'duration_years':1,'shock_pct':50})
    b=next(x for x in r['baseline']['rows'] if x['year']==2027)
    s=next(x for x in r['stressed']['rows'] if x['year']==2027)
    assert float(s['remaining_debt_end'])>float(b['remaining_debt_end'])
    assert s['debt_cash_payments']==b['debt_cash_payments']

@pytest.mark.parametrize('mode', ['medical_shock','one_time_cost'])
def test_extra_costs_cannot_be_negative(mode):
    p=sample();sc={'type':mode,'start_year':2027,'duration_years':1}
    sc['extra_monthly' if mode=='medical_shock' else 'extra_once']='-1'
    with pytest.raises(ValidationError):project(p,[sc],years=2)

from retirepilot.financial_references_v24 import employee_cpf_schedule_2026_27

def test_employee_cpf_schedule_dated_cohort_transition():
    # 1970 worker above 55 through 2026 and 2027; only reviewed OW tier.
    r=employee_cpf_schedule_2026_27(dob='1970-03-01',residency='SG',pr_cpf_year=None,
        months_and_wages=[{'month':'2026-11','ordinary_wages':'4000'},
                          {'month':'2027-02','ordinary_wages':'4000'}])
    assert r['status']=='bounded_reference' and r['months_count']==2
    assert r['months'][0]['worker_rate_pct']=='18' and r['months'][1]['worker_rate_pct']=='19'
    assert r['worker_total_sgd']=='1480.00'

def test_employee_cpf_schedule_blocks_missing_pr_year():
    r=employee_cpf_schedule_2026_27(dob='1974-05-20',residency='PR',pr_cpf_year=None,
        months_and_wages=[{'month':'2026-11','ordinary_wages':'4000'}])
    assert r['status']=='requires_review'

from retirepilot.assistant import regulated_or_execution_request,answer

@pytest.mark.parametrize('q',[
 'Should I buy shares in ABC Corp?',
 'Recommend a unit trust to invest in',
 'Which ETF should I buy?',
 'Transfer money from my CPF OA automatically',
 'I want guaranteed profits from a fund',
])
def test_regulated_advice_or_execution_guard(q):
    assert regulated_or_execution_request(q)
    r=answer(sample(),q)
    assert r['escalate'] is True


def test_vault_persistent_only_with_same_key(tmp_path):
    p=sample();key=Fernet.generate_key();path=tmp_path/'private'/'store.sqlite'
    v=LocalVault(path,key=key)
    for pid in ('P1','P2'):v.grant_consent(p['id'],pid,'household_planning',explicit=True)
    v.put_profile(p);v.close()
    v=LocalVault(path,key=key)
    assert v.get_profile(p['id'])==p
    v.close()
    v=LocalVault(path,key=Fernet.generate_key())
    with pytest.raises(VaultError,match='decrypt'):v.get_profile(p['id'])
    v.close()


def test_vault_cannot_verify_unapproved_action(tmp_path):
    p=sample();v=setup_vault(tmp_path)
    try:
        for pid in ('P1','P2'):v.grant_consent(p['id'],pid,'household_planning',explicit=True)
        v.grant_consent(p['id'],'P1','action_tracking',explicit=True)
        v.put_profile(p)
        v.create_action(p['id'],'P1','A2','Check statement','Confirm official figure')
        with pytest.raises(VaultError,match='Invalid state'):v.transition_action(p['id'],'A2','verified',actor='assistant',evidence_ref='x',verifier='other')
    finally:v.close()

def test_vault_purges_memory_and_actions_on_purpose_withdrawal(tmp_path):
    p=sample();v=setup_vault(tmp_path)
    try:
        for pid in ('P1','P2'):v.grant_consent(p['id'],pid,'household_planning',explicit=True)
        v.grant_consent(p['id'],'P1','local_memory',explicit=True)
        v.grant_consent(p['id'],'P1','action_tracking',explicit=True)
        v.put_profile(p)
        v.save_memory(p['id'],'P1','M100','Review retirement age')
        v.create_action(p['id'],'P1','A100','Review CPF','Confirm details')
        v.revoke_consent(p['id'],'P1','local_memory')
        v.revoke_consent(p['id'],'P1','action_tracking')
        assert v.db.execute('SELECT COUNT(*) FROM memory').fetchone()[0]==0
        assert v.db.execute('SELECT COUNT(*) FROM action').fetchone()[0]==0
        assert v.get_profile(p['id'])==p  # Consent for planning was not withdrawn
    finally:v.close()
