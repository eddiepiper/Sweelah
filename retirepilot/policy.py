"""Narrow, sourced Singapore CPF reference rules. Not official eligibility or payment calculation.

Rules are effective-dated and return 'requires_review' for unsupported or unknown cases.
"""
from __future__ import annotations
from datetime import date
from .core import age_on
from .statutory_2026 import _band_index

SOURCES={
 'CPF_EMPLOYEE_2026':'https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay',
 'CPF_EMPLOYEE_2027':'https://www.cpf.gov.sg/service/article/what-are-the-changes-to-the-cpf-contribution-rates-for-senior-workers-that-will-take-effect-from-1-january-2027',
 'CPF_BRS':'https://www.cpf.gov.sg/service/article/how-much-is-my-basic-retirement-sum',
 'CPF_LIFE_AGE':'https://www.cpf.gov.sg/service/article/when-can-i-start-receiving-my-cpf-life-payouts',
 'CPF_PLATFORM_OPT':'https://www.cpf.gov.sg/employer/platform-operators/obligations/which-platform-workers-should-receive-cpf-contributions'
}

REFERENCE_RULES=[
 {'id':'CPF-EMP-2026','version':'2026-01','valid_from':'2026-01-01','valid_until':'2027-01-01','source':SOURCES['CPF_EMPLOYEE_2026'],'verified':'Official page reviewed 2026-11-03','scope':'SG citizen / PR third year onward; wages > SGD 750 per month'},
 {'id':'CPF-EMP-2027','version':'2027-01','valid_from':'2027-01-01','valid_until':'2028-01-01','source':SOURCES['CPF_EMPLOYEE_2027'],'verified':'Official published 2027 rate change reviewed 2026-11-03','scope':'SG citizen / PR third year onward; wages > SGD 750 per month'},
 {'id':'CPF-BRS-COHORT','version':'2026-11','valid_from':'2026-01-01','valid_until':None,'source':SOURCES['CPF_BRS'],'verified':'Official page reviewed 2026-11-03','scope':'2026 and 2027 age-55 BRS/FRS reference only'},
 {'id':'CPF-LIFE-PAYOUT-AGE','version':'2026-11','valid_from':'2026-01-01','valid_until':None,'source':SOURCES['CPF_LIFE_AGE'],'verified':'Official page reviewed 2026-11-03','scope':'Payout-start age only, not payout amount or inclusion'},
 {'id':'CPF-PLATFORM-COHORT','version':'2026-11','valid_from':'2025-01-01','valid_until':None,'source':SOURCES['CPF_PLATFORM_OPT'],'verified':'Official page reviewed 2026-11-03','scope':'Birth cohort and irreversible opt-in distinction only, not contribution rate calculation'}]

def policy_reference(profile:dict) -> dict:
    asof=date.fromisoformat(profile['as_of'])
    people=[]
    for p in profile['persons']:
        years=age_on(p['dob'],asof)
        out={'id':p['id'],'age':years,'residency':p.get('residency'), 'references':[]}
        if p.get('residency') in ('SG','PR'):
            age55_year=date.fromisoformat(p['dob']).year+55
            if age55_year in (2026,2027):
                brs={2026:110200,2027:114100}[age55_year]
                out['references'].append({'policy':'CPF-BRS-COHORT','status':'reference_only','turns_55':age55_year,'brs_sgd':brs,'frs_sgd':brs*2,'source':SOURCES['CPF_BRS'],
                                          'note':'Reference sum is not individual retirement adequacy or official account balance.'})
            if 65<=years<=70:
                out['references'].append({'policy':'CPF-LIFE-PAYOUT-AGE','status':'requires_official_confirmation','age_window':'65-70','source':SOURCES['CPF_LIFE_AGE'],
                                          'note':'Eligibility, actual payout and plan choice must be checked on official CPF services.'})
            if p.get('residency')=='PR' and (p.get('pr_cpf_year') is None or int(p['pr_cpf_year'])<3):
                out['references'].append({'policy':'CPF-EMP-2026','status':'requires_review', 'source':SOURCES['CPF_EMPLOYEE_2026'],
                                          'note':'PR CPF contribution year unverified or graduated first/second year; no standard-rate inference.'})
            if asof.year in (2026,2027) and (p.get('residency')=='SG' or (p.get('residency')=='PR' and int(p.get('pr_cpf_year') or 0)>=3)):
                # Month-after-birthday implementation, not simple integer-age boundaries.
                bands=([(17,20),(16,18),(12.5,12.5),(9,7.5),(7.5,5)] if asof.year==2026
                       else [(17,20),(16.5,19),(13,13),(9,7.5),(7.5,5)])
                idx=_band_index(p['dob'],asof.year,asof.month,[55,60,65,70])
                emp,worker=bands[idx]
                ref='CPF_EMPLOYEE_2026' if asof.year==2026 else 'CPF_EMPLOYEE_2027'
                out['references'].append({'policy':'CPF-EMP-'+str(asof.year),'status':'reference_only',
                                          'employer_pct':emp,'employee_pct':worker,'source':SOURCES[ref],
                                          'note':'SG citizen / PR third year onward and monthly OW >750; annual ceilings, AW, and lower-wage tiers need official computation.'})
        else:
            out['references'].append({'policy':'CPF','status':'requires_review','note':'Do not presume Singapore CPF participation for foreign residents.'})
        people.append(out)
    platform=[]
    for i in profile.get('income_streams',[]):
        if i.get('type')!='platform':continue
        owner=next(p for p in profile['persons'] if p['id']==i['owner_id'])
        birth=date.fromisoformat(owner['dob'])
        mandatory=birth>=date(1995,1,1)
        if mandatory:status='mandatory_increased_contributions_cohort'
        elif i.get('platform_opt_in') is True:status='reported_opted_in_requires_confirmation'
        elif i.get('platform_opt_in') is False:status='reported_not_opted_in_requires_confirmation'
        else:status='opt_in_unknown'
        platform.append({'income_id':i['id'],'status':status,'source':SOURCES['CPF_PLATFORM_OPT'],
                         'note':'No platform CPF statutory amount calculated; FEDA, applicable rates, tiers and per-operator amounts require official calculator.'})
    return {'as_of':profile['as_of'],'people':people,'platform_income_references':platform,
            'rulebook_version':'SG-policy-reference-2026-11-03-v2.3','status':'reference_only_not_eligibility','sources':REFERENCE_RULES}
