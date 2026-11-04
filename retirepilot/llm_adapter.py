"""OPTIONAL experimental Responses API explanation adapter.

Disabled unless enabled in environment AND explicitly requested per action.
Synthetic profiles only. Sends only a local deterministic answer for rewording,
not raw household PII, not an action/tool request. The live provider was not tested.
"""
from __future__ import annotations
import json,os,urllib.request
from .assistant import answer

URL='https://api.openai.com/v1/responses'
class ModelDisabledError(RuntimeError):pass


def explain_synthetic(profile:dict, question:str, explicit_consent:bool=False, sender=None) -> dict:
    if not profile.get('id','').startswith('RP-SYNTH-'):
        raise ModelDisabledError('External model adapter accepts synthetic fixture IDs only')
    if not explicit_consent:
        raise ModelDisabledError('Explicit model-send consent required for this request')
    if os.environ.get('RETIREPILOT_EXPERIMENTAL_LLM')!='1':
        raise ModelDisabledError('Experimental external model connection disabled by default')
    api_key=os.environ.get('OPENAI_API_KEY')
    model=os.environ.get('RETIREPILOT_LLM_MODEL')
    if not api_key or not model:raise ModelDisabledError('Explicit API key and model setting required')
    deterministic=answer(profile,question)
    # Sends the deterministic response, which can contain aggregate financial amounts from synthetic fixtures; never raw records or identifiers.
    system=('You are an explanation rewriter in an educational Singapore financial-planning demo. '
            'Rewrite only the supplied grounded answer in plain language. Do not add facts, amounts, benefits, recommendations, products, '
            'transactions, eligibility claims or external sources. Never imply regulated financial advice. Keep it under 130 words.')
    body={'model':model,'instructions':system,
          'input':'User question (synthetic): '+question[:280]+'\nVerified local deterministic response to rephrase: '+deterministic['reply'],
          'max_output_tokens':220,'store':False}
    req=urllib.request.Request(URL,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+api_key},method='POST')
    send=sender or urllib.request.urlopen
    try:
        response=send(req,timeout=15)
        content=json.loads(response.read().decode('utf-8'))
    except Exception as e:
        raise ModelDisabledError('External model request failed; no result accepted') from e
    texts=[]
    for item in content.get('output',[]):
        for seg in item.get('content',[]):
            if seg.get('type')=='output_text':texts.append(seg.get('text',''))
    if not texts:raise ModelDisabledError('No valid text returned from model')
    return {'reply':' '.join(texts)[:1200],'grounded_source_reply':deterministic['reply'], 'sources':deterministic.get('sources',[]),
            'mode':'experimental_external_llm_rewrite_synthetic_only','warning':'Model-generated wording is not independently verified. Use the deterministic source reply for authoritative amounts.'}
