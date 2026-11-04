"""Grounded deterministic guidance and optional LLM interface boundary.
The default assistant is deliberately rule-based: no external model, no customer-data transfer.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
import re
from .core import monthly_snapshot,project,dec
from .adapter import classify_household

BLOCKED_TERMS=('which stock should i buy','buy this stock','guaranteed return','what insurance should i buy','sell my cpf','automatically transfer')
ADVICE_PATTERNS=(
    r'\b(?:buy|sell|pick|choose|recommend|allocate|switch|invest in)\b.{0,80}\b(?:stock|shares?|etf|bond|fund|crypto|policy|insurance|unit trust)\b',
    r'\b(?:which|best|what)\b.{0,40}\b(?:stock|shares?|etf|insurance|fund)\b.{0,40}\b(?:buy|choose|select|get)\b',
    r'\b(?:transfer|withdraw|top up|redeem)\b.{0,80}\b(?:cpf|account|ra|oa|srs)\b',
    r'\b(?:guarantee|guaranteed)\b.{0,60}\b(?:returns?|profits?|interest)\b',
)

def regulated_or_execution_request(q:str)->bool:
    return any(term in q.lower() for term in BLOCKED_TERMS) or any(re.search(pattern,q.lower()) for pattern in ADVICE_PATTERNS)



def plan_actions(profile, classification=None, snapshot=None):
    snapshot=snapshot or monthly_snapshot(profile)
    classification=classification or classify_household(profile)
    actions=[]
    def add(priority,title,reason,status='suggested',category='financial_planning'):
        actions.append({'priority':priority,'title':title,'reason':reason,'status':status,'category':category,'requires_user_approval':True,'verified_complete':False})
    if snapshot['expenses_monthly'] is None:add(1,'Record essential household expenses','A cash-flow and retirement projection requires actual or estimated recurring spending.')
    if snapshot['liquid_assets'] is None:add(1,'Record accessible cash and investments','Without accessible assets, emergency runway and bridge funding cannot be assessed.')
    if snapshot['cpf_balances_reported'] is None:add(1,'Review your own CPF balances','No CPF balances were supplied. Use the official CPF portal; do not share Singpass credentials.')
    if any('platform CPF opt-in status unknown' in w for w in snapshot['warnings']):add(1,'Verify platform-worker CPF contribution status','Rates differ by qualifying platform worker cohort and opt-in status; do not infer amounts.',category='policy_review')
    if snapshot['monthly_surplus'] is not None and dec(snapshot['monthly_surplus'])<0:add(1,'Review monthly cash shortfall','Recorded cash outflow exceeds recorded cash income in the current snapshot.')
    if snapshot['essential_cash_runway_months'] is not None and snapshot['essential_cash_runway_months']<3:add(1,'Review near-term liquidity and essential expenses','Available liquid funds cover fewer than 3 months of recorded essential outflows; the three-month threshold is an illustrative planning prompt.')
    if any('fewer than 6 months' in w for w in snapshot['warnings']):add(2,'Add more variable-income history','At least six monthly observations are needed for the current prototype to attempt volatility classification.')
    if not any(i['type']=='cpf_life' for i in profile.get('income_streams',[])):add(2,'Retrieve an official CPF retirement payout estimate','This prototype does not derive CPF LIFE payments from RA balances.',category='policy_review')
    if profile.get('liabilities'):add(3,'Review mortgage and debt expiry dates','Debt payments are included in cash flow, but full amortisation and CPF-funded payments need further modelling.')
    if not actions:add(3,'Recheck your financial plan periodically','Review material household, employment, spending or asset changes.')
    return sorted(actions,key=lambda a:(a['priority'],a['title']))


def answer(profile,question):
    if not isinstance(question,str) or not question.strip():return {'reply':'Ask about cash flow, household finances, retirement, CPF, or what action to take next.','sources':[],'mode':'local_grounded_assistant'}
    q=question.lower()
    sn=monthly_snapshot(profile);cl=classify_household(profile);acts=plan_actions(profile,cl,sn)
    if regulated_or_execution_request(q):
        return {'reply':'I can explain the factors and trade-offs, but I cannot recommend specific investments, insurance policies, or execute transfers. Consult a properly authorised adviser for product-specific guidance.','sources':[],'mode':'local_grounded_assistant','escalate':True}
    if any(word in q for word in ('cpf','payout','ra balance')):
        msg=('Your reported CPF balance is '+sn['cpf_balances_reported']+' SGD. ' if sn['cpf_balances_reported'] is not None else 'Your CPF balances have not been supplied. ')
        msg+='I cannot derive your CPF LIFE payout. Check an official CPF payout estimate and the applicable cohort rules before using it in your retirement scenario.'
        return {'reply':msg,'sources':['https://www.cpf.gov.sg/service/article/when-can-i-start-receiving-my-cpf-life-payouts','https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month'],'mode':'local_grounded_assistant'}
    if any(word in q for word in ('retire','retirement','65','future','scenario')):
        if sn['expenses_monthly'] is None or sn['liquid_assets'] is None:return {'reply':'I cannot responsibly produce a retirement projection until you supply spending and liquid-asset data. '+acts[0]['reason'],'sources':[],'mode':'local_grounded_assistant'}
        pr=project(profile,years=15)
        return {'reply':f"Under the illustrative 15-year assumptions, accessible assets end at SGD {pr['end_accessible_balance']} and cumulative uncovered cash need is SGD {pr['cumulative_unfunded_cash_need']}. These are deterministic model outputs, not a CPF prediction or an investment guarantee. Missing statutory deductions, CPF LIFE estimates or future household changes may materially alter the result.",'sources':[],'mode':'local_grounded_assistant'}
    if any(word in q for word in ('persona','profile','archetype','classif')):
        top=cl['user_visible_top_three']; names=', '.join(x['id']+' '+x['name'] for x in top) if top else 'No sufficiently evidenced matches yet'
        return {'reply':f'Possible planning patterns (provisional): {names}. Every one of the 96 definitions was evaluated. They are descriptive, not confidence scores, verified eligibility, advice or a priority ranking.','sources':[],'mode':'local_grounded_assistant'}
    if any(word in q for word in ('next','action','priority','what should')):
        return {'reply':'Your next review actions: '+ '; '.join(x['title'] for x in acts[:3])+'. These are information-gathering or review suggestions, not executed actions.','sources':[],'mode':'local_grounded_assistant'}
    if any(word in q for word in ('cash','income','monthly','spend','surplus','budget')):
        sur=sn['monthly_surplus'] if sn['monthly_surplus'] is not None else 'unknown (expenses missing)'
        return {'reply':f"Reported current monthly net cash income is SGD {sn['net_cash_income_monthly'] or 'unknown'}; expenses are SGD {sn['expenses_monthly'] or 'unknown'}; debt cash payments are SGD {sn['debt_cash_payments_monthly'] or 'unknown'}; resulting monthly surplus is {sur}. Income-stream worker CPF, taxes and actual operating costs are user-reported, not statutory estimates.",'sources':[],'mode':'local_grounded_assistant'}
    return {'reply':'I can assess your cash flow, show provisional persona matches, compare retirement scenarios and identify missing information. I cannot verify personal CPF eligibility, predict investment markets or provide regulated product advice. Ask what to review first or how a change in income affects cash flow.','sources':[],'mode':'local_grounded_assistant'}
