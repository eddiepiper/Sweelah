"""Audit of all 96 persona score definitions. NO empirical calibration is asserted."""
import json,collections,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rules=json.loads((ROOT/'retirepilot/retirepilot_rules_v1.2.json').read_text())
weights=collections.Counter();missing=[];rows=[]
for pid,p in sorted(rules['personas'].items()):
    w=tuple(c['weight'] for c in p['criteria'])
    weights[w]+=1
    refs=[x['predicate'].lstrip('!') for x in p['criteria']]+[p['gate'].lstrip('!'),p['exclusion'].lstrip('!')]
    miss=[x for x in refs if x not in rules['predicates']]
    if miss:missing.append({'id':pid,'predicates':miss})
    rows.append({'id':pid,'name':p['name'],'gate':p['gate'],'exclusion':p['exclusion'],
                 'weights':list(w),'score_mathematics_valid':sum(w)==100,
                 'empirical_calibration':'NOT DONE','independent_labelled_profiles':0,
                 'domain_approval':'PENDING','source':'Proposed product hypothesis'})
report={'date':'2026-11-03','persona_count':len(rows),'predicate_count':len(rules['predicates']),
        'missing_predicate_references':missing,'weight_patterns':[{'weights':list(k),'personas':v} for k,v in weights.items()],
        'all_persona_weights_unvalidated':True,'empirical_accuracy_estimate':None,
        'meaning_of_score':'Weighted observed match similarity, NOT probability or retirement readiness',
        'required_next_research':'Blind-labelled cases, age/income/employment/household stratification, review of fairness and thresholds',
        'personas':rows}
(ROOT/'audit/score_calibration_review_v24.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ('persona_count','predicate_count','weight_patterns','missing_predicate_references','all_persona_weights_unvalidated')},indent=2))
