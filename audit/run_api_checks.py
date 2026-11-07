"""Local-only synthetic API smoke checks, no external financial records."""
import json, subprocess, time, urllib.request, urllib.error, os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
port=8769
base=f'http://127.0.0.1:{port}'
proc=subprocess.Popen(['python','-m','uvicorn','retirepilot.api:app','--host','127.0.0.1','--port',str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
results=[]
def call(name,route,obj=None,expected=200):
    payload=None if obj is None else json.dumps(obj).encode('utf8')
    req=urllib.request.Request(base+route,data=payload,headers={'Content-Type':'application/json'} if payload else {},method='POST' if payload else 'GET')
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            status=r.status; data=json.loads(r.read()) if route!='/ ' else {}
    except urllib.error.HTTPError as e:
        status=e.code;data=json.loads(e.read())
    assert status==expected,(name,status,expected,data)
    results.append({'case':name,'status':status,'expected':expected,'pass':True})
    return data
try:
    for _ in range(50):
        try:call('sample GET','/api/sample');break
        except Exception:time.sleep(.1)
    else:raise RuntimeError('No localhost API available')
    p=json.loads((root/'data/mixed_income_household.json').read_text())
    r=call('synthetic evaluation','/api/evaluate',{'profile':p,'years':2})
    assert r['classification']['evaluated']==96
    q=dict(p);q['id']='REAL-USER'
    call('non-synthetic profile blocked','/api/evaluate',{'profile':q,'years':2},403)
    call('non-synthetic assistant blocked','/api/ask',{'profile':q,'question':'CPF'},403)
    call('synthetic assistant','/api/ask',{'profile':p,'question':'How is my cash flow?'})
    call('negative care expense rejected','/api/evaluate',{'profile':p,'years':1,'scenarios':[{'type':'care_shock','start_year':2026,'duration_years':1,'extra_monthly':'-50'}]},422)
    q=json.loads(json.dumps(p));q['assets'][0].pop('value')
    call('missing asset rejected','/api/evaluate',{'profile':q,'years':1},422)
    q=json.loads(json.dumps(p));q.pop('income_streams')
    res=call('missing income blocks projection','/api/evaluate',{'profile':q,'years':1})
    assert res['projection']['status']=='blocked_missing_required_data' and res['cash_flow']['net_cash_income_monthly'] is None
    q=json.loads(json.dumps(p));q.pop('liabilities')
    res=call('missing debt blocks projection','/api/evaluate',{'profile':q,'years':1})
    assert res['projection']['status']=='blocked_missing_required_data' and res['cash_flow']['debt_cash_payments_monthly'] is None
    q=json.loads(json.dumps(p));q['persons'][1].pop('consent_for_household_planning');q['persons'][1].pop('cpf_balances')
    call('adult consent enforcement','/api/evaluate',{'profile':q,'years':1},422)
    tax=call('IRAS chargeable-income reference','/api/reference',{'synthetic_profile_id':p['id'],'kind':'resident_tax','params':{'chargeable_income':'120000','year_of_assessment':2026,'resident_confirmed':True,'chargeable_income_confirmed':True}})
    assert tax['tax_before_rebates_sgd']=='7950.00'
    call('real profile reference rejected','/api/reference',{'synthetic_profile_id':'REAL-USER','kind':'resident_tax','params':{}},403)
    guide=call('synthetic progressive guide','/api/guide',{'profile':p,'question':'What should I review next?'})
    assert guide['financial_actions_executed'] is False
    care_request={'synthetic_profile_id':'RP-SYNTH-S016','params':{'additional_care_cost_monthly':'1200','months':12}}
    care=call('S016 synthetic cost preview','/api/scenarios/S016/preview',care_request)
    assert care['extra_monthly_cost']=='1200.00' and care['period_cash_cost']=='14400.00' and care['months']==12
    assert care['synthetic_only'] is True and care['may_post_to_household_projection'] is False
    assert care['status']=='LIMITED_RECURRING_COST_PREVIEW_ONLY'
    assert all(word in ' '.join(care['limitations']).lower() for word in ['subsidy','insurance','wage loss','entitlement'])
    call('S016 missing cost refused','/api/scenarios/S016/preview',{'synthetic_profile_id':'RP-SYNTH-S016','params':{'months':12}},422)
    call('S016 zero cost refused','/api/scenarios/S016/preview',{'synthetic_profile_id':'RP-SYNTH-S016','params':{'additional_care_cost_monthly':0,'months':12}},422)
    call('S016 boolean duration refused','/api/scenarios/S016/preview',{'synthetic_profile_id':'RP-SYNTH-S016','params':{'additional_care_cost_monthly':'1200','months':True}},422)
    call('S016 real profile refused','/api/scenarios/S016/preview',{'synthetic_profile_id':'REAL-USER','params':care_request['params']},403)
    subcent=call('S016 subcent cost refused','/api/scenarios/S016/preview',{'synthetic_profile_id':'RP-SYNTH-S016','params':{'additional_care_cost_monthly':'1.005','months':12}},422)
    assert subcent=={'detail':'Enter an amount with up to 2 decimal places, for example 1200.50.'}
    cents=call('S016 cents displayed consistently','/api/scenarios/S016/preview',{'synthetic_profile_id':'RP-SYNTH-S016','params':{'additional_care_cost_monthly':'1.50','months':12}})
    assert cents['extra_monthly_cost']=='1.50' and cents['period_cash_cost']=='18.00'
    print(json.dumps({'result':'PASS','total':len(results),'checks':results},indent=2))
    (root/'audit/api_evidence.json').write_text(json.dumps({'result':'PASS','total':len(results),'checks':results},indent=2))
finally:
    proc.terminate()
    try:proc.wait(timeout=4)
    except:proc.kill()
