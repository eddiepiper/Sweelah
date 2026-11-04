"""Synthetic, ephemeral consent -> profile -> action workflow smoke demonstration."""
from __future__ import annotations
import json,tempfile
from pathlib import Path
from cryptography.fernet import Fernet
from retirepilot.local_vault_v24 import LocalVault
from retirepilot.planner_session_v24 import guided_reply
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'data/mixed_income_household.json').read_text())
with tempfile.TemporaryDirectory(prefix='retirepilot-synthetic-') as td:
    v=LocalVault(Path(td)/'private'/'vault.sqlite',key=Fernet.generate_key())
    for person in ('P1','P2'):v.grant_consent(p['id'],person,'household_planning',explicit=True)
    v.grant_consent(p['id'],'P1','local_memory',explicit=True)
    v.grant_consent(p['id'],'P1','action_tracking',explicit=True)
    v.put_profile(p)
    v.save_memory(p['id'],'P1','M1','Goal: review retirement age 65')
    v.create_action(p['id'],'P1','ACT-001','Review official CPF statement','Validate reported retirement balances')
    v.transition_action(p['id'],'ACT-001','approved',actor='synthetic-user',approval=True)
    v.transition_action(p['id'],'ACT-001','in_progress',actor='synthetic-user')
    v.transition_action(p['id'],'ACT-001','reported_complete',actor='synthetic-user')
    action=v.transition_action(p['id'],'ACT-001','simulated_verified',actor='synthetic-user',verifier='synthetic-second-reviewer',evidence_ref='SYNTHETIC-OFFICIAL-REF-001')
    response=guided_reply(v.get_profile(p['id']),'What should I review next?')
    print(json.dumps({'mode':'synthetic_ephemeral_demo','profile_stored_encrypted':True,
       'local_memory_count':len(v.list_memory(p['id'],'P1')),'action_status':action['status'],
       'action_verification_is_synthetic_only':True,'assistant_executes_financial_actions':response['financial_actions_executed'],
       'audit_entries':len(v.list_audit_events())},indent=2))
    v.delete_profile(p['id']);v.close()
