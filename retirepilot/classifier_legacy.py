"""RetirePilot classification proof-of-concept, NOT financial advice or policy eligibility.
Run: python retirepilot_classifier_v1_2.py [optional_profile.json]
Rules: retirepilot_rules_v1.2.json (snapshot generated from Master Library v1.1 + audit corrections).
"""
import json,sys
from pathlib import Path
RULES=Path(__file__).with_name('retirepilot_rules_v1.2.json')
C=json.loads(RULES.read_text())
P=C['predicates']; R=C['personas']
POLICY=json.loads(Path(__file__).with_name('matching_policy_v2.2.json').read_text())
MIN_COVERAGE=int(POLICY['minimum_evidence_coverage'])
MIN_MATCH_SCORE=int(POLICY['minimum_match_score'])

def predicate(token,profile):
    if token.startswith('!'):
        x=predicate(token[1:],profile)
        return None if x is None else not x
    p=P[token];value=profile.get(p['field'])
    if value is None:return None
    op=p['op']; expected=p['expected']
    if op=='EQ':
        if expected in ('true','false'):
            return value is (expected=='true') if isinstance(value,bool) else None
        return str(value)==expected
    if op=='IN': return str(value) in expected.split(';')
    if op=='HAS':
        return expected in value if isinstance(value,(list,tuple,set)) else str(value)==expected
    if op in ('GTE','GT','LTE','LT'):
        try:
            v=float(value);e=float(expected)
        except (ValueError,TypeError):return None
        return {'GTE':v>=e,'GT':v>e,'LTE':v<=e,'LT':v<e}[op]
    raise ValueError(f'Invalid predicate comparator: {op}')

def evaluate_persona(pid,profile):
    r=R[pid]
    gate=predicate(r['gate'],profile)
    exclusion=predicate(r['exclusion'],profile)
    vals=[predicate(z['predicate'],profile) for z in r['criteria']]
    known=sum(z['weight'] for z,v in zip(r['criteria'],vals) if v is not None)
    hit=sum(z['weight'] for z,v in zip(r['criteria'],vals) if v is True)
    score=round(100*hit/known,2) if known else None
    if gate is False or exclusion is True:status='excluded'
    elif gate is None or exclusion is None:status='pending_gate'
    elif known<MIN_COVERAGE:status='provisional'
    elif score is None or score<MIN_MATCH_SCORE:status='not_relevant'
    else:status='matched'
    return {'id':pid,'name':r['name'],'status':status,'observed_score':score if status in ('matched','provisional','not_relevant') else None,
            'evidence_coverage':known,'gate':gate,'exclusion':exclusion,
            'predicates':[{**z,'observed':v} for z,v in zip(r['criteria'],vals)],
            'rule_version':C['version'],'engine_version':'2.2.0-remediated'}

def classify(profile):
    all_results=[evaluate_persona(pid,profile) for pid in sorted(R)]
    matches=sorted((x for x in all_results if x['status']=='matched'),key=lambda x:(-x['observed_score'],-x['evidence_coverage'],x['id']))
    return {'rule_version':C['version'],'engine_version':'2.2.0-remediated','matching_policy_version':POLICY['policy_version'],'minimum_match_score':MIN_MATCH_SCORE,'minimum_evidence_coverage':MIN_COVERAGE,'evaluated':len(all_results),'user_visible_top_three':matches[:3],
            'all_results':all_results,'counts':dict((k,sum(x['status']==k for x in all_results)) for k in ('matched','provisional','pending_gate','excluded','not_relevant')),
            'warnings':['Proposed persona-match model only; 60-point threshold and weights not validated','Top-three sorted by observed match score, NOT validated financial urgency','Does not evaluate Singapore scheme eligibility, retirement readiness or recommend investments']}

def make_fixture(pid,positive=True):
    r=R[pid]; tokens=[r['gate']]+([x['predicate'] for x in r['criteria']] if positive else [])
    record={}
    for tok in tokens:
        p=P[tok];field=p['field'];op=p['op'];expected=p['expected']
        if op=='EQ':val=(expected=='true') if expected in ('true','false') else expected
        elif op=='HAS':val=[expected]
        elif op=='IN':val=expected.split(';')[0]
        elif op in ('GT','GTE','LT','LTE'):
            number=float(expected)
            val=number+(1 if op=='GT' else -1 if op=='LT' else 0)
        else:raise ValueError(op)
        if field in record and record[field]!=val:
            if isinstance(val,list) and isinstance(record[field],list):record[field]=sorted(set(record[field]+val))
            else:raise ValueError(f'Contradictory positive fixture for {pid}: {field}: {record[field]} vs {val}')
        else:record[field]=val
    return record

if __name__=='__main__':
    if len(sys.argv)>1: profile=json.loads(Path(sys.argv[1]).read_text())
    else: profile=make_fixture('C02')
    print(json.dumps(classify(profile),indent=2))
