import json, csv, hashlib, shutil, os
from pathlib import Path
from datetime import datetime
r=Path(__file__).resolve().parents[1]
a=r/'audit'
risks=[
('VAL-01','Critical','Privacy','Secondary adult income/assets could be included without their consent flag','Fixed in v2.1 for referenced adult financial records','Code flags only; not authenticated consent or PDPA sign-off'),
('VAL-02','High','Data accuracy','Unreported income streams previously treated as zero','Fixed in v2.1: no cash result and projection blocked','Explicit empty list still means reported zero income'),
('VAL-03','High','Data accuracy','Unreported liabilities previously treated as zero','Fixed in v2.1: debt unknown and projection blocked','Liability inventory cannot be verified by software'),
('VAL-04','High','Data integrity','Missing asset values caused KeyError and server error','Fixed in v2.1: structured validation error','User may still supply inaccurate asset estimates'),
('VAL-05','High','Data integrity','Missing income gross/cost could default to zero','Fixed in v2.1: explicit value required for listed streams','Other optional deductions remain user-reported and may be omitted'),
('VAL-06','High','Scenario maths','Negative care expense artificially improved outcomes','Fixed in v2.1: rejected','Full scenario contract and economic realism not independently validated'),
('VAL-07','Medium','CPF reference','Third-year-plus Singapore PR omitted from 2026 contribution reference','Fixed in v2.1: standard reference only when PR year explicitly 3+','No statutory per-person contribution calculation'),
('VAL-08','High','Demo boundary','Unauthenticated API could accept non-synthetic identifier','Partially mitigated: synthetic fixture ID gate added','ID is spoofable; real-data exposure risk remains without security stack'),
('VAL-09','High','Financial model','Single blended return applied to cash and investments','Open: methodology approval required','Cash yield/investment return and allocation must be modelled separately'),
('VAL-10','High','Financial model','2026 as-of November modelled as full annual year with Dec 31 age','Open: pro-rata monthly model required','Retirement and income cessation can shift a full year'),
('VAL-11','Critical','Financial model','No validated statutory CPF, CPF LIFE, tax, mortgage amortisation, insurance','Open: authoritative calculator reconciliation required','No individual retirement readiness certification'),
('VAL-12','High','Classifier','96 weights and mandatory conditions were not calibrated using genuine cases','Open: specialist review + real-world validation','498 legacy fixtures are largely derived from the rules themselves'),
('VAL-13','Critical','Security','No user authentication, encryption/retention system, identity-based consent audit','Open: secure architecture + PDPA DPIA + penetration test','Never expose prototype to internet or real financial data'),
('VAL-14','Critical','Regulatory','MAS financial-advisory perimeter and action restrictions not cleared','Open: qualified Singapore legal/compliance sign-off','No product-specific recommendation functionality approved'),
('VAL-15','High','Accessibility / usability','Main onboarding consists of editable raw JSON','Open: replace with progressive guided accessible forms','Not suitable for general 45+ consumers yet'),
('VAL-16','High','Accessibility / usability','No Mandarin, Malay, Tamil journeys or readability validation','Open: localisation + participant comprehension tests','No multilingual release readiness'),
('VAL-17','High','Testing','Browser-based interaction/screenshot blocked by environment policy','Blocked: separate browser QA environment required','No WCAG 2.2 AA audit can be claimed'),
('VAL-18','High','Research','48 actual interviews and observed task completions are not conducted','Open: recruit, consent, moderate, analyse','Do not count interview slots as respondents'),
('VAL-19','Medium','Model governance','External LLM adapter remains disabled; no live prompt injection assessment','Open: design governed provider + tool boundary','Not a live generative AI agent'),
('VAL-20','Medium','UI disclosure','Export button implied anonymisation without verification','Fixed in v2.1: clearer warning label','No guarantee export lacks sensitive entered data')
]
cols=['risk_id','severity','area','finding','current_status','residual_issue']
(a/'risk_register.json').write_text(json.dumps([dict(zip(cols,x)) for x in risks],indent=2))
with (a/'risk_register.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(cols);w.writerows(risks)
urls={
 'CPF-RATES-2026':'https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay',
 'CPF-RATES-2027':'https://www.cpf.gov.sg/member/infohub/educational-resources/new-cpf-contribution-rates-for-senior-workers',
 'CPF-SUMS':'https://www.cpf.gov.sg/member/infohub/educational-resources/what-is-the-cpf-retirement-sum',
 'CPF-PLATFORM':'https://www.cpf.gov.sg/member/growing-your-savings/cpf-contributions/saving-as-a-platform-worker',
 'CPF-PLATFORM-2026':'https://www.cpf.gov.sg/service/article/what-is-the-change-in-cpf-contribution-rates-for-platform-workers-from-january-2026',
 'HDB-LBS':'https://www.hdb.gov.sg/managing-my-home/retirement-planning/monetising-flat-for-retirement/lease-buyback-scheme-lbs',
 'MAS-FAA':'https://www.mas.gov.sg/regulation/capital-markets/apply-for-licensing-or-registration-of-capital-market-entities/financial-advisers',
 'MAS-ADVICE-SCOPE':'https://www.mas.gov.sg/regulation/guidelines/guidelines-on-provision-of-financial-advisory-service',
 'PDPA':'https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act'
}
policies=[
('SGP-01','2026 employee CPF aggregate reference','<=55 employer 17% worker 20%; >55-60 16/18; >60-65 12.5/12.5; >65-70 9/7.5; >70 7.5/5. Age, monthly earnings >$750, third-year+ PR context.',urls['CPF-RATES-2026'],'Official table anchor checked','Reference-only; wages bands, ceilings, actual contributions not implemented'),
('SGP-02','2027 senior worker CPF change','2027 >55-60 employer 16.5%, worker 19%; >60-65 employer 13%, worker 13% for wage tier noted.',urls['CPF-RATES-2027'],'Official announcement checked','Not encoded in 2026-only policy engine'),
('SGP-03','Age-55 BRS / FRS and current ERS','2026 BRS 110200, FRS 220400, ERS 440800; 2027 BRS 114100, FRS 228200, ERS 456400.',urls['CPF-SUMS'],'Official anchor checked','Not a retirement readiness metric; no personalised entitlement'),
('SGP-04','Platform work categorisation','Qualifying ride-hail/delivery managed by operator. Born before 1995 can opt into increased contributions; irreversible. 2026 contributions vary by age, earnings and status.',urls['CPF-PLATFORM'],'Official definitions checked','Rates not calculated; do not conflate property agent with platform worker'),
('SGP-05','Platform FEDA','Cars 60%, motorcycles/PAB 35%, bicycles/walking 20% statutory deductions of gross for CPF net earnings.',urls['CPF-PLATFORM'],'Official anchor checked','Actual operating costs remain separate; no calculator implementation'),
('SGP-06','HDB Lease Buyback screen','Owners age >=65; at least one citizen; household monthly income <=16000; and flat/occupation/lease restrictions.',urls['HDB-LBS'],'Official anchor checked','Not an official eligibility decision or payout estimate'),
('SGP-07','FAA regulated financial advice','Regulated FAA activities generally need licence or exemption, and representatives where applicable.',urls['MAS-FAA'],'Official anchor checked','Legal determination of RetirePilot product boundaries remains outstanding'),
('SGP-08','Financial advice definition','MAS provides two-stage assessment under Guidelines on Provision of Financial Advisory Service.',urls['MAS-ADVICE-SCOPE'],'Official anchor checked','Legal counsel must apply to product features'),
('SGP-09','PDPA protection','Consent, notification, purpose, accuracy, protection, retention and access/correction considerations.',urls['PDPA'],'Official framework cited','DPIA and production security design not completed')
]
pcols=['id','module','verified_anchor','official_url','evidence_status','implementation_boundary']
(a/'policy_register.json').write_text(json.dumps([dict(zip(pcols,x)) for x in policies],indent=2))
with (a/'policy_register.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(pcols);w.writerows(policies)
segments=[('Salaried workers',8),('Platform / gig workers',6),('Property / commission / SEP',6),('Pre-retirees 55-64',6),('Retirees 65+',6),('Family transitions / caregivers',5),('Lower-income / hardship',6),('PR / cross-border / complex',5)]
slots=[]
languages=['English']*24+['Mandarin']*12+['Malay']*6+['Tamil']*6
ages=['45-49','50-54','55-59','60-64','65-69','70+']*8
n=0
for seg,count in segments:
 for j in range(count):
  slots.append({'slot_id':f'R{n+1:03d}','primary_quota':seg,'target_age_band':ages[n],'target_language':languages[(n*11)%48],
                'recruitment_status':'Not recruited','consent_status':'Not sought','interview_status':'Not conducted',
                'participant_id':'','date':'','comprehension_result':'','task_result':'','notes':''})
  n+=1
assert len(slots)==48
(a/'research_slots.json').write_text(json.dumps(slots,indent=2))
with (a/'research_slots.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=slots[0].keys());w.writeheader();w.writerows(slots)
tasks=[
 ('U01','45-49 salaried parent','Complete guided intake without providing CPF credentials','Not executable: current UI only edits raw JSON','P0'),
 ('U02','52-year-old agent + Grab worker','Record separate revenue/cost history for each income stream','Partially demonstrable via JSON','P0'),
 ('U03','Unreported CPF balance','Understand why personal CPF LIFE payout cannot be calculated','Desk-test only','P0'),
 ('U04','Spouse refuses data consent','Confirm household financial data is not accessed','Structural validation test PASS, authentication not built','P0'),
 ('U05','Senior aged 66 with CPF estimate','Differentiate supplied CPF estimate from inferred certainty','Synthetic code test only','P0'),
 ('U06','Low-income senior with inadequate liquid reserves','Find assistance path without recommending an investment product','Not implemented','P0'),
 ('U07','Age 55 CPF milestone','Distinguish official policy reference from actual entitlement','Desk-test only','P0'),
 ('U08','Person with low digital confidence','Complete progressive onboarding with no JSON expertise','Not implemented','P0'),
 ('U09','Mandarin, Malay and Tamil users','Read and explain personalised outputs in preferred language','Not implemented','P1'),
 ('U10','Keyboard-only / screen-reader user','Navigate, operate scenarios and access chart information','Browser execution blocked','P0'),
 ('U11','User changes incorrectly reported income','Observe immediate recalculation of all 96 matches','Backend code test PASS, UI interaction unverified','P1'),
 ('U12','Variable-income downturn','Explain why stress result changed and what was assumed','No participant task completion data','P0')
]
tcols=['task_id','target_persona','task','current_evidence','priority']
(a/'usability_tasks.json').write_text(json.dumps([dict(zip(tcols,x)) for x in tasks],indent=2))
with (a/'usability_tasks.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(tcols);w.writerows(tasks)
summary={
 'audit_date':'2026-11-03', 'prototype':'RetirePilot Phases 7-8 audit build v2.1',
 'new_pytest_passed':256,'new_pytest_failed':0,'legacy_rule_contract_passed':498,'legacy_rule_contract_failed':0,'local_api_smoke_passed':10,
 'source_reviewed_policy_items':len(policies), 'risks':len(risks),
 'fixed_or_mitigated_risks':sum('Fixed in' in x[4] or 'Partially mitigated' in x[4] for x in risks),
 'research_slots_planned':len(slots),'actual_interviews':0,'actual_usability_sessions':0,
 'browser_interaction_status':'blocked_by_administrator',
 'independent_vera_qa':'not performed',
 'financial_domain_signoff':'not performed',
 'mas_legal_signoff':'not performed',
 'security_pdpa_signoff':'not performed',
 'internal_synthetic_demo':'conditional_go',
 'external_research_with_real_financial_records':'no_go',
 'external_consumer_pilot':'no_go'
}
(a/'execution_evidence.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
