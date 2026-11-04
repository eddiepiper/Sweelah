"""Local guided financial-planning assistant with explicit state and non-executing actions.

No live LLM, bank integrations, Singpass calls or regulated investment recommendations.
Store is a synthetic-only encrypted local vault, not production cloud infrastructure.
"""
from __future__ import annotations
from .core import validate
from .assistant import answer,plan_actions
from .adapter import classify_household
from .service import evaluate
from .local_vault_v24 import LocalVault, VaultError

QUESTION_FLOW=(
 ('income_streams','Please add each income source separately, including commissions or platform work.'),
 ('expenses','Please provide essential and nonessential monthly household expenses.'),
 ('liabilities','Please list mortgages and other debts, or explicitly confirm none.'),
 ('assets','Please list accessible savings, investments and other assets, or explicitly confirm none.'),
 ('goal','What age do you hope to stop paid work, and how much do you want to spend during retirement?'),
)

def next_question(profile:dict):
    validate(profile)
    for key,text in QUESTION_FLOW:
        if key not in profile:return {'field':key,'question':text,'reason':'Input is missing, not zero'}
    for p in profile['persons']:
        if p['id']==profile['primary_id'] and 'cpf_balances' not in p:
            return {'field':'persons.primary.cpf_balances','question':'Would you like to enter your latest CPF OA, SA, MA and RA balances from your own official statement?','reason':'CPF balances are currently unknown; no payout will be inferred'}
    return {'field':None,'question':'Review your recorded plan and identify the most important change to test next.','reason':'No core profile group is missing'}

def guided_reply(profile:dict,question:str):
    validate(profile)
    result=answer(profile,question)
    result['next_question']=next_question(profile)
    result['financial_actions_executed']=False
    result['requires_user_review']=True
    return result

def build_review_actions(profile:dict):
    return plan_actions(profile)

def save_review_action(vault:LocalVault, profile_id:str, person_id:str, action_id:str, title:str,reason:str):
    return vault.create_action(profile_id,person_id,action_id,title,reason)
