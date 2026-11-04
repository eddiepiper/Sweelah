"""Independent regression expectations for approved D001-D007: synthetic only."""
import json
from pathlib import Path
from datetime import date
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
from retirepilot.api import app
from retirepilot.core import validate,ValidationError,project
from retirepilot.classifier_legacy import classify,make_fixture
from retirepilot.service import evaluate, public_persona_summary
from retirepilot.local_vault_v24 import LocalVault,VaultError
from retirepilot.priority_scenarios_v27 import PRIORITY_IDS,preview_priority_scenario
ROOT=Path(__file__).resolve().parents[1]
SAMPLE=json.loads((ROOT/'data/mixed_income_household.json').read_text())

def test_p0_terminal_month_proration_independent_reference():
    x=deepcopy(SAMPLE)
    x['as_of']='2027-01-01'
    x['goal']['projection_end_age']=53  # birthday on 20 May 2027
    x['goal']['retirement_age']=65
    # Remove all earnings except a flat 7200 monthly input for exact algebra.
    x['income_streams']=[{'id':'I-TEST','owner_id':'P1','type':'salary','gross_monthly':'7200',
          'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'}]
    result=project(x)
    # Jan-Apr full + May 1-19 inclusive (exclusive upper boundary May 20).
    # 7200 * (4 + 19/31) == 33212.903225806...
    assert result['rows'][0]['year']==2027
    assert result['rows'][0]['income']=='33212.90'

def test_p0_terminal_birthday_on_first_excludes_final_month():
    x=deepcopy(SAMPLE);x['as_of']='2027-01-01';x['persons'][0]['dob']='1974-05-01'
    x['goal']['projection_end_age']=53;x['goal']['retirement_age']=65
    x['income_streams']=[{'id':'I-TEST','owner_id':'P1','type':'salary','gross_monthly':'7200',
          'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'}]
    assert project(x)['rows'][0]['income']=='28800.00'

def test_p0_terminal_expense_proration_matches_income():
    x=deepcopy(SAMPLE);x['as_of']='2027-01-01';x['goal']['projection_end_age']=53
    x['expenses']=[{'id':'E-test','category':'other','amount_monthly':'3100'}]
    # (4+19/31)*3100=14300.00; 2027 inflation applies as offset zero
    assert project(x)['rows'][0]['spending']=='14300.00'

def test_provisional_personas_hide_numbers_from_public_evaluation():
    result=evaluate(SAMPLE,[],1)['classification']
    assert result['evaluated']==96
    assert result['display_policy']=='descriptions_only_unvalidated'
    assert 'minimum_match_score' not in result and 'all_results' not in result and 'counts' not in result
    assert all('observed_score' not in x and 'evidence_coverage' not in x for x in result['user_visible_top_three'])
    assert all(x['status']=='provisional_pattern' for x in result['user_visible_top_three'])
    # Internal rules still evaluate 96 with raw weights for audit.
    assert classify(make_fixture('A01'))['evaluated']==96

def test_provisional_persona_ui_no_score_badges():
    html=(ROOT/'retirepilot/ui.html').read_text()
    assert "esc(p.observed_score)" not in html
    assert "esc(p.evidence_coverage)" not in html

def test_cpf_life_source_required_for_projections():
    x=deepcopy(SAMPLE)
    x['income_streams'].append({'id':'CPF-TEST','owner_id':'P1','type':'cpf_life','gross_monthly':'1800',
          'starts_age':65,'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'})
    with pytest.raises(ValidationError,match='estimate source required'):validate(x)
    x['income_streams'][-1]['source']='published_table_example'
    with pytest.raises(ValidationError,match='estimate source required'):validate(x)
    x['income_streams'][-1]['source']='synthetic_user_provided_estimate'
    assert validate(x) is not None

def test_cpf_life_source_synthetic_not_allowed_for_real_identifier():
    x=deepcopy(SAMPLE);x['id']='UNVERIFIED-REAL'
    x['income_streams'].append({'id':'CPF-TEST','owner_id':'P1','type':'cpf_life','gross_monthly':'1800',
          'starts_age':65,'source':'synthetic_user_provided_estimate',
          'cash_deductions_monthly':'0','worker_cpf_monthly':'0','tax_reserve_monthly':'0'})
    with pytest.raises(ValidationError,match='estimate source required'):validate(x)

def test_no_household_sharing_without_real_identity_provider(tmp_path):
    vault=LocalVault(tmp_path/'household.sqlite',key=Fernet.generate_key())
    with pytest.raises(VaultError,match='sharing blocked'):
        vault.share_household_records('RP-SYNTH-001','P2',identity_evidence='I verified',consent_evidence='I agree')
    vault.close()

def test_release_controls_are_fail_closed():
    resp=TestClient(app).get('/api/release-controls')
    assert resp.status_code==200
    data=resp.json()
    assert data['household_sharing']=='blocked' and data['external_consumer_pilot']=='NO_GO'
    assert data['identity_verification']=='not_integrated'

@pytest.mark.parametrize('sid',PRIORITY_IDS)
def test_all_five_priorities_have_explicit_contract(sid):
    x=preview_priority_scenario(sid,{}) if sid=='S012' else None
    if x:assert x['status'].startswith('BLOCKED')
    assert sid in ('S020','S030','S004','S016','S012')

def test_downsize_requires_official_cpf_refund():
    req={'sale_price':'900000','sale_costs':'20000','outstanding_mortgage':'250000',
         'cpf_refund_official':'200000','replacement_home_total_cost':'300000',
         'cpf_refund_source':'member_transcribed_official_cpf_property_refund'}
    r=preview_priority_scenario('S020',req)
    assert r['sale_cash_proceeds_after_cpf_refund']=='430000.00'
    assert r['cash_after_replacement_purchase']=='130000.00'
    req['cpf_refund_source']='estimated_by_AI'
    with pytest.raises(ValidationError,match='official member-supplied'):preview_priority_scenario('S020',req)

def test_payout_timing_never_infers_cpf_amounts():
    r=preview_priority_scenario('S030',{'estimate_source':'member_transcribed_official_cpf_estimate',
                                       'official_monthly_at_65':'1500','official_monthly_at_70':'2100'})
    assert r['monthly_cash_difference_70_less_65']=='600.00'
    with pytest.raises(ValidationError,match='member-transcribed'):preview_priority_scenario('S030',{
        'estimate_source':'published_table_example','official_monthly_at_65':'1500','official_monthly_at_70':'2100'})

def test_part_time_preview_net_cash_math_and_missing_input():
    v=preview_priority_scenario('S004',{'current_net_earned_cash_monthly':'5600',
                                      'part_time_net_earned_cash_monthly':'3000','months':6})
    assert v['period_cash_change']=='-15600.00'
    with pytest.raises(ValidationError):preview_priority_scenario('S004',{'current_net_earned_cash_monthly':'5600','months':6})

def test_parent_care_sensitivity_only():
    x=preview_priority_scenario('S016',{'additional_care_cost_monthly':'1200','months':12})
    assert x['period_cash_cost']=='14400.00'
    assert x['may_post_to_household_projection'] is False

def test_divorce_requires_legal_and_consent_inputs_not_formula():
    x=preview_priority_scenario('S012',{'estimated_property_split':'50/50'})
    assert x['status']=='BLOCKED_PENDING_LEGAL_AND_HOUSEHOLD_CONSENT'
    assert 'cash_after_replacement_purchase' not in x

def test_five_scenarios_not_claimed_as_complete():
    assert all(preview_priority_scenario(sid,kwargs)['may_post_to_household_projection'] is False for sid,kwargs in [
        ('S004',{'current_net_earned_cash_monthly':'100','part_time_net_earned_cash_monthly':'50','months':3}),
        ('S012',{}),
        ('S016',{'additional_care_cost_monthly':'100','months':3}),
        ('S020',{'sale_price':'500000','sale_costs':'10000','outstanding_mortgage':'100000',
                 'cpf_refund_official':'50000','replacement_home_total_cost':'300000',
                 'cpf_refund_source':'member_transcribed_official_cpf_property_refund'}),
        ('S030',{'estimate_source':'member_transcribed_official_cpf_estimate',
                 'official_monthly_at_65':'1000','official_monthly_at_70':'1500'}),
    ])

def test_approved_decisions_registry_complete():
    j=json.loads((ROOT/'docs/APPROVED_DECISIONS_v2.7.json').read_text())
    assert [d['answer'] for d in j['decisions']]==['1A','2A','3A','4A','5A','6A','7A']
    assert j['external_pilot']=='NO_GO'
