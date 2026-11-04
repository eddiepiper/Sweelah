"""Independent-contract and misuse tests for v2.5, synthetic-only.

Expected CPF and IRAS values here are transcribed from published rate/tax tables;
these are NOT certificates from CPF/IRAS and do not cover all cases.
"""
import json
from pathlib import Path
import pytest
from cryptography.fernet import Fernet
from retirepilot.core import compare, ValidationError
from retirepilot.financial_references_v24 import resident_tax_reference
from retirepilot.local_vault_v24 import LocalVault, VaultError
from retirepilot.statutory_2026 import employee_ow_cpf

ROOT=Path(__file__).resolve().parents[1]

def fixture():
    return json.loads((ROOT/'data/mixed_income_household.json').read_text())

# Source: IRAS resident rates, YA 2024 onwards, values independently transcribed.
@pytest.mark.parametrize('chargeable,official_tax',[('20000','0.00'),('30000','200.00'),
    ('40000','550.00'),('80000','3350.00'),('120000','7950.00'),
    ('160000','13950.00'),('200000','21150.00'),('240000','28750.00'),
    ('280000','36550.00'),('320000','44550.00'),('500000','84150.00'),
    ('1000000','199150.00')])
def test_iras_independent_rate_anchor(chargeable,official_tax):
    actual=resident_tax_reference(chargeable_income=chargeable,year_of_assessment=2027,
        resident_confirmed=True,chargeable_income_confirmed=True)
    assert actual['tax_before_rebates_sgd']==official_tax

# Source: CPF Board employer 2026 rates; 2027 senior-worker announcement.
@pytest.mark.parametrize('dob,year,worker,employer',[('1980-01-01',2026,'1600.00','1360.00'),
    ('1970-01-01',2026,'1440.00','1280.00'),('1965-01-01',2026,'1000.00','1000.00'),
    ('1960-01-01',2026,'600.00','720.00'),('1955-01-01',2026,'400.00','600.00'),
    ('1970-01-01',2027,'1520.00','1320.00'),('1965-01-01',2027,'1040.00','1040.00')])
def test_cpf_independent_full_rate_anchor(dob,year,worker,employer):
    r=employee_ow_cpf(dob=dob,residency='SG',month=f'{year}-11',monthly_ordinary_wages='8000')
    assert r['status']=='bounded_reference'
    assert (r['worker_share_sgd'],r['employer_share_sgd'])==(worker,employer)

@pytest.mark.parametrize('scenario,expected',[ 
    ({'type':'job_loss','start_year':2027,'income_ids':['MISSING'],'shock_pct':100},'unknown income_ids'),
    ({'type':'commission_drop','start_year':2027,'income_ids':['I3'],'shock_pct':40},'incompatible income types'),
    ({'type':'rental_vacancy','start_year':2027,'income_ids':['I1'],'shock_pct':100},'incompatible income types'),
    ({'type':'platform_cost_shock','start_year':2027,'income_ids':['I1'],'shock_pct':50},'incompatible income types'),
    ({'type':'rent_increase','start_year':2027,'shock_pct':20},'no rent expense'),
    ({'type':'commission_drop','start_year':2022,'duration_years':1,'shock_pct':50},'period ends before assessment year')])
def test_invalid_stress_scenarios_rejected(scenario,expected):
    p=fixture()
    p['income_streams'].append({'id':'I3','owner_id':p['primary_id'],'type':'salary','gross_monthly':'1500',
       'cash_deductions_monthly':'0','worker_cpf_monthly':'300','tax_reserve_monthly':'0'})
    with pytest.raises(ValidationError,match=expected):compare(p,[scenario],years=3)

@pytest.mark.parametrize('scenario',[{'type':'housing_payment_shock','start_year':2027,'shock_pct':20},
                                    {'type':'mortgage_rate_shock','start_year':2027,'shock_pct':30}])
def test_mortgage_scenario_without_mortgage_rejected(scenario):
    p=fixture()
    p['liabilities']=[]
    with pytest.raises(ValidationError,match='no mortgage liability'):compare(p,[scenario],years=2)

def test_cash_only_market_crash_is_nonoperative_not_fake_loss():
    p=fixture()
    for a in p['assets']:
        if a['type']=='investment': a['type']='cash'
    r=compare(p,[{'type':'market_crash','start_year':2027,'shock_pct':50}],years=3)
    assert r['delta_end_accessible_balance']=='0.00'

def test_simulation_is_not_independent_verification(tmp_path):
    p=fixture()
    v=LocalVault(tmp_path/'synthetic.db',key=Fernet.generate_key())
    try:
        for person in p['persons']:
            v.grant_consent(p['id'],person['id'],'household_planning',explicit=True)
        v.put_profile(p)
        v.grant_consent(p['id'],p['primary_id'],'action_tracking',explicit=True)
        v.create_action(p['id'],p['primary_id'],'ACTION-002','Review CPF','Compare official statement')
        v.transition_action(p['id'],'ACTION-002','approved',actor='synthetic_user',approval=True)
        v.transition_action(p['id'],'ACTION-002','in_progress',actor='synthetic_user')
        v.transition_action(p['id'],'ACTION-002','reported_complete',actor='synthetic_user')
        with pytest.raises(VaultError,match='Invalid state transition'):
            v.transition_action(p['id'],'ACTION-002','verified',actor='synthetic_user',
                verifier='text-that-pretends-to-be-independent',evidence_ref='fake-receipt')
        with pytest.raises(VaultError,match='Simulation requires synthetic evidence'):
            v.transition_action(p['id'],'ACTION-002','simulated_verified',actor='synthetic_user',
                verifier='test_verifier',evidence_ref='unverified-receipt')
        x=v.transition_action(p['id'],'ACTION-002','simulated_verified',actor='synthetic_user',
            verifier='mock_verifier',evidence_ref='synthetic-receipt-001')
        assert x['verified_complete'] is False
        assert x['status']=='simulated_verified'
        assert x['simulation']['simulation_only'] is True
    finally: v.close()
