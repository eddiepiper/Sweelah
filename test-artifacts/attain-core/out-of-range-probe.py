"""Probe /api/evaluate (synthetic RP-SYNTH profiles only) for out-of-range ages."""
import json, sys
from fastapi.testclient import TestClient
from retirepilot.api import app
c = TestClient(app, raise_server_exceptions=False)
Z = {'inflation_pct':'0','nominal_return_pct':'0','cash_yield_pct':'0','income_growth_pct':'0'}
def prof(dob='1974-05-20', as_of='2027-01-01', end=60):
    return {'id':'RP-SYNTH-PROBE','as_of':as_of,'currency':'SGD','primary_id':'P1',
            'persons':[{'id':'P1','role':'primary','dob':dob,'residency':'SG','marital_status':'single'}],
            'relationships':[],'income_streams':[{'id':'I1','owner_id':'P1','type':'rental','gross_monthly':'100','worker_cpf_monthly':'0','tax_reserve_monthly':'0','cash_deductions_monthly':'0','operating_costs_monthly':'0'}],
            'expenses':[{'id':'E1','category':'other','amount_monthly':'50','person_id':'P1'}],'liabilities':[],
            'assets':[{'id':'A1','type':'cash','owners':{'P1':'1'},'value':'1000','accessible':True}],
            'goal':{'projection_end_age':end},'assumptions':dict(Z)}
cases = []
for v in [8025, 8026, 9000, 9999, 10**6, -1974, -1975, -10**6, 2**31-1, 2**62, 2**63-1, 2**63, 10**20]:
    p = prof(); p['income_streams'][0]['starts_age'] = v; cases.append((f'starts_age={v} (year {1974+v})', p))
for v in [7990, 7991, 9000, 10**6, 2**63, 10**20]:
    p = prof(); p['expenses'][0]['end_person_age'] = v; cases.append((f'end_person_age={v} (year {1974+v})', p))
p = prof('9950-01-15', '9990-06-01', 95); cases.append(('dob 9950-01-15, as_of 9990-06-01, projection_end_age 95 (horizon year 10045)', p))
for name, p in cases:
    r = c.post('/api/evaluate', json={'profile': p, 'years': 5})
    body = r.text
    detail = json.loads(body).get('detail') if body.startswith('{') and r.status_code != 200 else ('<ok>' if r.status_code == 200 else body[:60])
    print(f'{r.status_code}  {name}  detail={detail!r}')
