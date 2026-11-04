from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'retirepilot/core.py'
s=p.read_text()
s=s.replace("        for f in ('gross_monthly','operating_costs_monthly','cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):\n            _positive_amount(inc,f,inc['id'])",
'''        if inc.get('gross_monthly') is None:
            raise ValidationError(f"{inc['id']}: gross_monthly required for a reported income stream; missing is unknown")
        if inc.get('type') in ('platform','commission','self_employed','business','rental') and inc.get('operating_costs_monthly') is None:
            # Do not equate unknown business/rental operating costs to zero.
            raise ValidationError(f"{inc['id']}: operating_costs_monthly required (explicit 0 permitted)")
        for f in ('gross_monthly','operating_costs_monthly','cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):
            _positive_amount(inc,f,inc['id'])''')
s=s.replace("        _positive_amount(item,'value',item['id'])\n        _validate_ownership(item,persons)",
'''        if item.get('value') is None:
            raise ValidationError(f"{item['id']}: asset value unknown; provide a documented estimate or omit the asset and mark the financial assessment incomplete")
        _positive_amount(item,'value',item['id'])
        _validate_ownership(item,persons)''')
s=s.replace("        _validate_ownership(item,persons)\n        if item.get('remaining_years') is not None",
'''        if item.get('balance') is None:
            raise ValidationError(f"{item['id']}: liability balance unknown; cannot assume zero")
        _validate_ownership(item,persons)
        if item.get('remaining_years') is not None''')
s=s.replace("    for r in profile.get('relationships',[]): \n        if r.get('from_id') not in persons:raise ValidationError('relationship from_id missing')",
'''    # Household membership is not consent to access another adult's financial records.
    asof_ages={p['id']:age_on(p['dob'],asof) for p in members}
    for person in members:
        pid=person['id']
        if pid==profile['primary_id'] or asof_ages[pid]<18:continue
        references=bool(person.get('cpf_balances')) or any(x.get('owner_id')==pid for x in profile.get('income_streams',[]))
        references=references or any(pid in x.get('owners',{}) for group in ('assets','liabilities') for x in profile.get(group,[]))
        references=references or any(x.get('person_id')==pid for x in profile.get('expenses',[]))
        references=references or any(x.get('covered_person_id')==pid for x in profile.get('protection',[]))
        if references and person.get('consent_for_household_planning') is not True:
            raise ValidationError(f'{pid}: explicit adult consent required for referenced financial records')
    for r in profile.get('relationships',[]): 
        if r.get('from_id') not in persons:raise ValidationError('relationship from_id missing')''')
s=s.replace("    return duration,shock\n", """    if s['type']=='care_shock':
        if s.get('extra_monthly') is None or dec(s['extra_monthly'])<0:
            raise ValidationError('care_shock.extra_monthly must be explicitly provided and nonnegative')
    if s.get('income_ids') is not None:
        if not isinstance(s['income_ids'],list) or any(not isinstance(v,str) for v in s['income_ids']):
            raise ValidationError('scenario income_ids must be an array of identifiers')
    return duration,shock
""")
p.write_text(s)
# Policy reference for PRs with explicitly verified 3rd+ CPF year, without inferring from PR status.
p=root/'retirepilot/policy.py';s=p.read_text()
s=s.replace("            if asof.year==2026 and p.get('residency')=='SG':", """            if p.get('residency')=='PR' and (p.get('pr_cpf_year') is None or int(p['pr_cpf_year'])<3):
                out['references'].append({'policy':'CPF-EMP-2026','status':'requires_review', 'source':SOURCES['CPF_EMPLOYEE_2026'],
                                          'note':'PR CPF contribution year unverified or graduated first/second year; no standard-rate inference.'})
            if asof.year==2026 and (p.get('residency')=='SG' or (p.get('residency')=='PR' and int(p.get('pr_cpf_year',0))>=3)):
""")
p.write_text(s)
# Mark research-only API as synthetic fixtures only to reduce accidental exposure of sensitive customer records.
p=root/'retirepilot/api.py';s=p.read_text()
s=s.replace("async def body_json(req):", """def require_synthetic_fixture(profile):
    if not isinstance(profile,dict) or not str(profile.get('id','')).startswith('RP-SYNTH-'):
        raise HTTPException(403,'Only synthetic fixture IDs accepted; never submit actual financial records')

async def body_json(req):""")
s=s.replace("        profile=data['profile']\n        scenarios=data.get('scenarios',[])","        profile=data['profile']\n        require_synthetic_fixture(profile)\n        scenarios=data.get('scenarios',[])")
s=s.replace("        if data.get('use_experimental_llm'):","        require_synthetic_fixture(data['profile'])\n        if data.get('use_experimental_llm'):")
p.write_text(s)
print('Patched core, policy, API')
