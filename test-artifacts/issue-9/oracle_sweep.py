import random
from datetime import date,timedelta
from calendar import monthrange
from decimal import Decimal as D, ROUND_HALF_UP
from retirepilot.core import project, age_on
def q(x):return x.quantize(D('0.01'),ROUND_HALF_UP)
def bday(dob,age):
    # birthday per age_on semantics: first date where age_on>=age
    b=date.fromisoformat(dob)
    try:return date(b.year+age,b.month,b.day)
    except ValueError:return date(b.year+age,3,1)
def oracle(asof,end,amt,stop=None,startd=None):
    by={}
    d=asof
    while d<end:
        if (stop is None or d<stop) and (startd is None or d>=startd):
            by[d.year]=by.get(d.year,D(0))+D(amt)/D(monthrange(d.year,d.month)[1])
        d+=timedelta(1)
    return {y:q(v) for y,v in by.items()}
random.seed(9)
bad=[]
dobs=['1974-05-20','1974-05-01','1974-05-31','1974-01-31','1976-02-29','1972-02-29','1974-12-31','1974-02-28','1975-03-01']
for dob in dobs:
  for asof in ['2026-11-03','2027-01-01','2026-12-31','2026-02-15','2028-02-29']:
    for kind,extra in [('income',{}),('expense',{}),('retire',{}),('start',{}),('endexp',{})]:
      a=date.fromisoformat(asof); age=age_on(dob,a)
      end_age=age+random.choice([1,2])
      hz=bday(dob,end_age)
      p={"id":"SYN","as_of":asof,"currency":"SGD","primary_id":"P1",
       "persons":[{"id":"P1","role":"primary","dob":dob,"residency":"SG","marital_status":"single"}],
       "relationships":[],"income_streams":[],"expenses":[],"liabilities":[],"assets":[],
       "goal":{"projection_end_age":end_age},"assumptions":{"inflation_pct":"0","nominal_return_pct":"0","cash_yield_pct":"0","income_growth_pct":"0"}}
      inc={"id":"I1","owner_id":"P1","type":"salary","gross_monthly":"7200","worker_cpf_monthly":"0","tax_reserve_monthly":"0","cash_deductions_monthly":"0","operating_costs_monthly":"0"}
      stop=startd=None
      if kind=='income':inc['type']='rental';p['income_streams']=[inc];key='income'
      if kind=='retire':p['goal']['retirement_age']=end_age;p['goal']['projection_end_age']=end_age+1;hz=bday(dob,end_age+1);stop=bday(dob,end_age);p['income_streams']=[inc];key='income'
      if kind=='start':inc['type']='rental';inc['starts_age']=end_age;p['goal']['projection_end_age']=end_age+1;hz=bday(dob,end_age+1);startd=bday(dob,end_age);p['income_streams']=[inc];key='income'
      if kind=='expense':p['expenses']=[{"id":"E1","category":"other","amount_monthly":"7200"}];key='spending'
      if kind=='endexp':p['expenses']=[{"id":"E1","category":"other","amount_monthly":"7200","person_id":"P1","end_person_age":end_age}];p['goal']['projection_end_age']=end_age+1;hz=bday(dob,end_age+1);stop=bday(dob,end_age);key='spending'
      try:r=project(p)
      except Exception as e:print('ERR',dob,asof,kind,e);continue
      o=oracle(a,hz,7200,stop,startd)
      for row in r['rows']:
        exp=o.get(row['year'],D('0.00'))
        if D(row[key])!=exp:bad.append((dob,asof,kind,end_age,row['year'],row[key],str(exp),str(D(row[key])-exp)))
for b in bad:print(b)
print(len(bad),'mismatches')
