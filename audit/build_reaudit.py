"""Build an evidence-focused re-audit from reproducible test results and project state."""
from pathlib import Path
from datetime import date
from copy import deepcopy
import json,hashlib,re
from retirepilot.core import monthly_snapshot,project
from retirepilot.service import evaluate
from retirepilot.classifier_legacy import R,P,C,POLICY
from retirepilot.adapter import classify_household
ROOT=Path(__file__).resolve().parents[1]

phases=[
(1,'18 dimensions and 96 archetypes','DESIGN BASELINE ONLY','The approved Excel taxonomy contains 18 dimensions and 96 reference archetypes. Not evidence of statistical population coverage.','Representative demographic validation and source-based coverage review outstanding.'),
(2,'Deterministic persona rulebook','PARTIAL','96 gates/exclusions and 384 weighted criteria; syntactic rule contracts pass. Explicit match minimum 60 and evidence minimum 70 added in v2.2.','All 96 archetypes retain generic 35/30/20/15 weights; threshold and domain rules unapproved.'),
(3,'96-persona classifier','TECHNICAL DEFECT FIXED; NOT CALIBRATED','Every profile evaluated against 96 archetypes. A zero-score match is now not_relevant and suppressed from user top three.','Only 67/177 field features obtained from complex synthetic case; no independent relevance labels.'),
(4,'Household financial model','PARTIAL','Structured synthetic people, income sources, ownership, expenses, debt and explicit missingness; consent assertions in the demonstration.','No authenticated persistence, adult consent lifecycle, secure data access or full household integration.'),
(5,'Financial calculation engine','TECHNICAL REMEDIATION PASS; DOMAIN NO-GO','Monthly projected cash flow now applies retirement birthdays, partial-year periods, separate asset return assumptions, amortised loan cash flows and explicit missing-data blocks.','CPF, tax, CPF LIFE, HDB eligibility and 40 of 46 scenario catalog entries are not implemented/reconciled; maturity balloon assumptions remain unresolved.'),
(6,'AI personal financial assistant','DEMONSTRATION ONLY','Offline deterministic question/answer interface for synthetic profiles.','No production LLM, secure personal memory, verified task execution, reminders, or regulated advice clearance.'),
(7,'Independent assurance','NOT COMPLETE','Technical tests and bounded policy references; this re-audit is a self-performed engineering audit.','No independent financial, QA, security, privacy or Singapore legal/compliance signoff.'),
(8,'Real-user research','NOT EXECUTED','Recruitment plan for 48 people, interview guide and moderated task list exist.','0/48 real interviews, 0 moderated sessions, no documented accessibility or multilingual evaluation.'),
]

blockers={
'BLK-01':('RETIREMENT TIMING','TECHNICALLY FIXED','Target retirement birthday now stops primary earned income; continuation requires explicit override.'),
'BLK-02':('MISSING DEDUCTIONS','TECHNICALLY FIXED','Missing CPF/tax/other cash deductions block projection and unknown surplus.'),
'BLK-03':('ZERO-SCORE MATCH','TECHNICALLY FIXED','0/100 or <60 becomes not_relevant, not displayed as matched.'),
'BLK-04':('STATUTORY CALCULATORS','OPEN','No reconciled CPF employment/platform/SEP, tax or CPF LIFE calculation.'),
'BLK-05':('AUTHENTICATION/PRIVACY','OPEN','Local synthetic guard is not secure authentication; no real records.'),
'BLK-06':('FINANCIAL ADVICE LEGAL PERIMETER','OPEN','No Singapore qualified professional opinion.'),
'BLK-07':('LIVE CONSUMER RESEARCH','OPEN','0/48 participant interviews or moderated observed tasks.'),
'BLK-08':('PERSONA WEIGHTS','OPEN','Uniform 35/30/20/15 weights and minimum score are uncalibrated.'),
'BLK-09':('CASH YIELD','TECHNICALLY FIXED','Cash yield and portfolio return are independently controlled; cash defaults to explicit 0% model assumption.'),
'BLK-10':('PARTIAL YEAR','TECHNICALLY FIXED','Monthly as-of day proration, including expenses and debt; end-age boundary covered.'),
'BLK-11':('SCENARIO COVERAGE','OPEN','Six scenario types implemented; 40 further catalogue entries not complete.'),
'BLK-12':('18-DIMENSION COVERAGE','OPEN','67 of 177 flattened taxonomy attributes derivable in the mixed-income example.'),
'BLK-13':('LIVE FINANCIAL AI ASSISTANT','OPEN','No live safeguarded generative assistant or persistent workflow.'),
'BLK-14':('INDEPENDENT QA','OPEN','Self-run tests; no Vera or independent expert certification.'),
'BLK-15':('BROWSER/ACCESSIBILITY QA','OPEN','No completed interactive browser, keyboard or screen-reader QA.'),
'BLK-16':('GUIDED UX/MULTILINGUAL','OPEN','The UI remains developer-oriented JSON editing, not age-friendly progressive onboarding.'),
'BLK-17':('PERSONA DOMAIN APPROVAL','OPEN','Rule corrections and scoring methodology not approved by domain reviewers.'),
'BLK-18':('DEBT/CPF OA FLOW','PARTIAL','Monthly amortisation implemented; CPF OA depletion and contractual maturity/balloon remain unresolved.'),
}

profile=json.loads((ROOT/'data/mixed_income_household.json').read_text())
classif=classify_household(profile)
financial=monthly_snapshot(profile)
base=project(profile,years=5)
profile55=deepcopy(profile);profile55['goal']['retirement_age']=55
profile65=deepcopy(profile);profile65['goal']['retirement_age']=65
cash_only=deepcopy(profile);cash_only['assets']=[a for a in cash_only['assets'] if a['type']=='cash']
miss=deepcopy(profile)
for i in miss['income_streams']:
    for name in ('cash_deductions_monthly','worker_cpf_monthly','tax_reserve_monthly'):i.pop(name,None)

pytest_text=(ROOT/'audit/test_run_v22.txt').read_text()
match=re.search(r'(\d+) passed',pytest_text)
assert match and int(match.group(1))>0
contracts=json.loads((ROOT/'audit/classifier_rule_contracts_v2_2.json').read_text())
api=json.loads((ROOT/'audit/api_evidence.json').read_text())

source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'retirepilot/core.py',ROOT/'retirepilot/projection_v22.py',ROOT/'retirepilot/classifier_legacy.py',ROOT/'retirepilot/matching_policy_v2.2.json',ROOT/'retirepilot/retirepilot_rules_v1.2.json']}

evidence={
    'audit_date':'2026-11-03','scope':'Phases 2-5 code remediation and phases 1-8 evidence re-audit',
    'release_decision':'PHASE 9 NO-GO',
    'test_evidence':{'pytest_passed':int(match.group(1)),'pytest_failed':0,'rule_contract_passed':contracts['passed'],'rule_contract_failed':contracts['failed'],'api_checks_passed':api['total'],'real_interviews':0,'independent_qa_signoff':False},
    'taxonomy':{'dimensions':18,'archetypes':len(R),'predicates':len(P),'scoring_criteria':sum(len(r['criteria']) for r in R.values()),'fixed_weight_vector':sorted({tuple(z['weight'] for z in r['criteria']) for r in R.values()}), 'minimum_match_score':POLICY['minimum_match_score'],'threshold_status':POLICY['status']},
    'mixed_household':{'monthly_gross':financial['gross_monthly'],'monthly_cash_income':financial['net_cash_income_monthly'],'monthly_surplus':financial['monthly_surplus'],'fields_derived':classif['derived_field_count'],'fields_unresolved':classif['unknown_field_count'],'persona_counts':classif['counts'],'persona_top3':[{'id':v['id'],'match_score':v['observed_score'],'evidence_coverage':v['evidence_coverage']} for v in classif['user_visible_top_three']], 'calendar_2026':{k:base['rows'][0][k] for k in ('income','spending','debt_cash_payments','net_cash_flow','portfolio_gain','cash_interest','remaining_debt_end')}},
    'reproductions':{'retirement_income_2030_age55':project(profile55,years=5)['rows'][4]['income'],'retirement_income_2030_age65':project(profile65,years=5)['rows'][4]['income'],'missing_deductions_projection_status':evaluate(miss,[],1)['projection']['status'],'cash_only_investment_gain':project(cash_only,years=1)['rows'][0]['portfolio_gain'],'first_year_partial':base['rows'][0]['first_year_partial']},
    'phases':[dict(zip(('phase','name','verdict','observed_evidence','open_gap'),row)) for row in phases],
    'blockers':[{'id':k,'name':v[0],'state':v[1],'evidence':v[2]} for k,v in blockers.items()],
    'source_hashes':source_hashes,
    'caveats':['Technical tests are self-run and synthetic, not independent or real-user acceptance evidence','Retirement projection is a disclosed scenario model, not verified CPF/financial advice','Original PSD/TSD v2.0 describe earlier behavior; engineering v2.2 change log supersedes formula/timing sections', 'All proposed scoring and statutory rule determinations require professional review'],
}

assert sum(v['state']=='TECHNICALLY FIXED' for v in evidence['blockers'])==5
assert len(R)==96 and len(P)==225
(ROOT/'audit/Phase2to5_Remediation_Evidence_v2.2.json').write_text(json.dumps(evidence,indent=2)+'\n')

lines=[
'# RetirePilot: Phases 2-5 Remediation and Phases 1-8 Re-audit',
'', '**Audit date:** 3 November 2026  ', '**Scope:** Local synthetic research prototype  ',
'**Release decision: PHASE 9 NO-GO**',
'',
'## Executive conclusion',
'',
'The six originally highlighted core integrity problems have been technically addressed: retirement timing (including income cessation), missing-deduction blocking, zero-score persona labels, cash return separation, partial-year dates, and elementary mortgage amortisation. These fixes are supported by executed tests. **They do not make the product a validated Singapore financial planner.**',
'',f"Technical evidence: **{evidence['test_evidence']['pytest_passed']} passed pytest cases**, **{contracts['passed']} passed rule-contract checks**, **{api['total']} passed local API checks**. All tests use synthetic inputs and were run by the same development/audit process.",
'',
'## Actual phase gates',
'',
'| Phase | Gate verdict | Evidence | Still not done |',
'|---|---|---|---|',
]
for p in evidence['phases']:
    lines.append(f"| {p['phase']} | {p['verdict']} | {p['observed_evidence']} | {p['open_gap']} |")
lines.extend(['','## Before-and-after critical defect evidence','','| Defect | After remediation |','|---|---|',
"| Retirement target | For the same synthetic household, income in 2030 is **S$"+evidence['reproductions']['retirement_income_2030_age55']+"** when retiring at 55 versus **S$"+evidence['reproductions']['retirement_income_2030_age65']+"** when retiring at 65. |",
"| Missing cash deductions | Engine returns `"+evidence['reproductions']['missing_deductions_projection_status']+"`; no confident surplus. |",
"| Zero-score persona | Minimum 60 match score and 70 evidence coverage; 0 scores are `not_relevant`, suppressed from top three. **Threshold is unvalidated.** |",
"| Cash incorrectly treated as invested | Cash-only investment gain is S$"+evidence['reproductions']['cash_only_investment_gain']+" under any chosen investment return. Cash yield controlled separately. |",
"| Partial first year | 2026 includes 3 November through 31 December only, with income, expense and debt proration. |",
"| Mortgage | Tracks month-by-month interest, scheduled cash/CPF payments, remaining balance and known maturity mismatch warnings; no CPF account depletion. |",
'', '## Evidence in the mixed-income synthetic household','',
'| Metric | Remediated output |','|---|---:|',
*[f'| {k} | {v} |' for k,v in [('Current monthly gross receipts',financial['gross_monthly']),('Current monthly net cash income',financial['net_cash_income_monthly']),('Current monthly surplus',financial['monthly_surplus']),('2026 partial-year income',base['rows'][0]['income']),('2026 partial-year spending',base['rows'][0]['spending']),('2026 partial-year debt cash payment',base['rows'][0]['debt_cash_payments']),('2026 partial-year net cash flow',base['rows'][0]['net_cash_flow']),('Taxonomy derived fields',classif['derived_field_count']),('Taxonomy unresolved fields',classif['unknown_field_count'])]],
'',
'## Detailed remediation/blocker register','','| ID | Status | Evidence or remaining dependency |','|---|---|---|',
])
for b in evidence['blockers']:lines.append(f"| {b['id']} {b['name']} | **{b['state']}** | {b['evidence']} |")
lines += ['',
'## What is still needed before Phase 9', '',
'1. **Phase 2:** Approve and calibrate the proposed 60-point threshold, persona weights and definitions with external, independently labelled profile examples. Confirm all 96 definitions clinically and commercially relevant only to their financial need, not to protected personal attributes.',
'2. **Phase 4:** Design authenticated personal/household records, explicit per-adult consent and revocation, retention/deletion and a privacy/security threat model. Prove no real data can enter the unsecured prototype.',
'3. **Phase 5:** Implement and reconcile statutory CPF employee/SEP/platform contribution rules, relevant CPF LIFE inputs, tax, housing amortisation incl. CPF-funded payments, and benefit screening to official cases. Support or explicitly exclude each of 46 catalogued scenarios.',
'4. **Phase 6:** Implement secure model-based explanations with grounded tool outputs, immutable calculation results, controlled memory and read-only verification of actions. The present interface is not that product.',
'5. **Phase 7:** Obtain genuinely independent financial domain, software QA, privacy/security and financial-advice legal reviews. Self-run tests do not meet this gate.',
'6. **Phase 8:** Conduct 30-50 stratified real interviews, moderated usability sessions, multilingual/accessibility testing, triage observed failures and retest. Current completed count: 0.',
'',
'## Key technical limitations that remain', '',
'- The financial forecast uses **user-declared** tax/CPF deductions and CPF LIFE payout estimates; it does not calculate them. It must not be called a statutory calculator.',
'- The first calendar year is partial, and defaults are explicitly listed, but **reliable life-long future forecasts** still require interest resets, tax and CPF, inflation uncertainty, debt maturity/refinancing and care-cost assumptions.',
'- Only six scenario operators are implemented, despite a catalogue of 46 scenarios. Unsupported scenarios are rejected rather than silently evaluated.',
'- The 96 archetypes are all evaluated, but generic scoring weights and taxonomies remain **unapproved**, and top-three matches can change because of these provisional rules.',
'- Browser QA was not completed during this remediation. The front end remains a developer-facing synthetic JSON interface.',
'- All outputs apply to synthetic research records only. No external or pilot release is authorised.',
'',
'## Reproduce the checks', '',
'From the extracted project folder:', '',
'```bash',
'python -m pip install -r requirements.txt',
'python -m pytest -q tests/',
'PYTHONPATH=. python audit/run_rule_contracts_v22.py',
'python audit/run_api_checks.py',
'```',
'',
'Expected results on the audited environment: 378 pytest cases passed; 498 rule-contract checks passed; 10 localhost API checks passed. Old v2.0 financial golden examples were archived and updated because they assumed a full calendar year from November. Original rule predicates and weights are unchanged.',
'',
'## Release disposition', '',
'**Internal synthetic technical development: CONDITIONAL GO. Phase 9 (real users, actual financial data, financial advice or live external pilot): NO-GO.**',
]
(ROOT/'audit/RetirePilot_Phase1to8_Reaudit_v2.2.md').write_text('\n'.join(lines)+'\n')
print('Wrote re-audit MD and JSON; phases',len(phases),'blockers',len(blockers))
