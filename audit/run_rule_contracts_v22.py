"""Independently executable rule-contract and regression suite, synthetic examples only."""
import json,hashlib,random
from pathlib import Path
from retirepilot.classifier_legacy import C,P,R,predicate,evaluate_persona,classify,make_fixture,MIN_COVERAGE
out=[]
def test(name,condition,detail=''):
    out.append({'test':name,'status':'PASS' if condition else 'FAIL','detail':str(detail)})
def false_value(p):
    op=p['op'];v=p['expected']
    if op=='EQ':return not(v=='true') if v in ('true','false') else '__other__'
    if op in ('HAS','IN'):return ['__other__'] if op=='HAS' else '__other__'
    x=float(v)
    if op=='GTE':return x-1
    if op=='GT':return x
    if op=='LTE':return x+1
    if op=='LT':return x

assert len(R)==96
for pid,r in sorted(R.items()):
    try:
        positive=make_fixture(pid)
        val=evaluate_persona(pid,positive)
        test(pid+'-positive',val['status']=='matched' and val['observed_score']==100 and val['evidence_coverage']==100,(val['status'],val['observed_score'],val['evidence_coverage']))
    except Exception as e:
        test(pid+'-positive',False,repr(e));positive={}
    g=P[r['gate']]
    negative={g['field']:false_value(g)}
    test(pid+'-negative',evaluate_persona(pid,negative)['status']=='excluded')
    test(pid+'-unknown',evaluate_persona(pid,{})['status']=='pending_gate')
    # Partial: gate plus first weighted criterion, independent of other criteria
    try:
        first=r['criteria'][0]['predicate'];f=P[first];partial=make_fixture(pid,positive=False)
        if f['field'] not in partial:
            v=make_fixture(pid,positive=True)[f['field']]
            partial[f['field']]=v
        v=evaluate_persona(pid,partial)
        test(pid+'-partial',v['status'] in ('provisional','matched','not_relevant') and v['evidence_coverage']<100 and v['observed_score'] is not None,(v['status'],v['evidence_coverage']))
    except Exception as e:test(pid+'-partial',False,repr(e))
# Completeness, consistency and correction tests
test('CATALOGUE-96',len(R)==96 and len(set(R))==96)
test('DIMENSIONS-18',len({f'D{i:02d}' for i in range(1,19)})==18 and all(p['dimension'] in {f'D{i:02d}' for i in range(1,19)} for p in P.values()))
test('PREDICATES-REFERENCED',all(t.lstrip('!') in P for r in R.values() for t in [r['gate'],r['exclusion']]+[x['predicate'] for x in r['criteria']]))
test('CRITERIA-384',sum(len(r['criteria']) for r in R.values())==384)
test('WEIGHTS-100',all(sum(x['weight'] for x in r['criteria'])==100 for r in R.values()))
test('EXCLUSIONS-CONSISTENT',all(r['exclusion']=='!'+r['gate'] for r in R.values()))
test('D06-REPAIRED',R['D06']['gate']=='individual_not_earning' and [x['predicate'] for x in R['D06']['criteria']].count('partner_earns')==1)
fixture=make_fixture('C02');one=classify(fixture);two=classify(dict(fixture))
test('ALL-96-IN-ONE',one['evaluated']==96 and len(one['all_results'])==96)
test('IDENTICAL-INPUTS',one==two)
test('TOP3-ONLY',len(one['user_visible_top_three'])<=3)
fixed=dict(fixture);gate=P[R['C02']['gate']];fixed[gate['field']]=false_value(gate)
test('FACT-CORRECTION',evaluate_persona('C02',fixture)['status']=='matched' and evaluate_persona('C02',fixed)['status']=='excluded')
test('MISSING-IS-NOT-ZERO',evaluate_persona('C02',{})['status']=='pending_gate')
# type mismatch boolean must return unknown not false
test('UNTRUSTED-BOOLEAN-TYPE',predicate('partner_earns',{'relationships.partner_has_income':'false'}) is None)
# Known gate, missing criteria -> no top-3 even if observed score appears 100
gateprofile=make_fixture('C02',positive=False)
test('LOW-EVIDENCE-SUPPRESSED',evaluate_persona('C02',gateprofile)['status']=='provisional' and 'C02' not in [x['id'] for x in classify(gateprofile)['user_visible_top_three']])
# Every canonical individual fixture must trigger own archetype in a full batch
for pid in sorted(R):
    try:
        batch=classify(make_fixture(pid))
        own=next(x for x in batch['all_results'] if x['id']==pid)
        test('BATCH-'+pid,batch['evaluated']==96 and own['status']=='matched' and own['observed_score']==100)
    except Exception as e:test('BATCH-'+pid,False,repr(e))
# Input immutability under classification
before=json.dumps(fixture,sort_keys=True);classify(fixture)
test('NO-INPUT-MUTATION',json.dumps(fixture,sort_keys=True)==before)
# Formal status counts total
x=classify({'person.age_years':52})
test('STATUS-TOTAL',sum(x['counts'].values())==96)
# Mixed income must not assign salary worker when only commission+platform present
mixed={'income_stream.trade':'property_agent','income_stream.type':['commission','platform'],'person.age_years':52,'relationships.dependent_children_count':2,'relationships.parent_support_active':True,'liabilities.active_mortgage':True,'assets.hdb_owner':True}
x=classify(mixed)
test('MIXED-INCOME-96',x['evaluated']==96)
test('NO-SALARY-ASSUMPTION',next(z for z in x['all_results'] if z['id']=='B06')['status']!='matched')
report={'title':'RetirePilot 96-Persona Classifier - Synthetic Technical Audit','version':C['version'],'source_sha256':C['source_sha256'],
        'engine_version':'2.2.0-remediated','tests_executed':len(out),'passed':sum(z['status']=='PASS' for z in out),'failed':sum(z['status']=='FAIL' for z in out),
        'failures':[z for z in out if z['status']=='FAIL'],
        'changes':C['changes'],
        'limitations':['Self-generated positive fixtures test internal consistency, not real-world persona validity','Input fields are flattened prototype values; real household data and one-to-many income provenance not implemented','Scores and thresholds are uncalibrated; no statistical representativeness or policy eligibility proof','Financial calculations are illustrative; independent QA, full consent controls and regulatory review are not completed']}
Path('audit/classifier_rule_contracts_v2_2.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('changes','failures')},indent=2))
if report['failures']:print('FAILURES',json.dumps(report['failures'][:25],indent=2))
