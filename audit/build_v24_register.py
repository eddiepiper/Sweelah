"""Append execution evidence to the existing RetirePilot master library (artifact_tool)."""
import json
from pathlib import Path
from artifact_tool import Blob, SpreadsheetFile
ROOT=Path(__file__).resolve().parents[1]
source=Path('/mnt/data/RetirePilot_Master_Library_v1.4_Policy_and_Gates.xlsx')
wb=SpreadsheetFile.import_xlsx(Blob.load(str(source)))

def add_sheet(name,headers,rows,widths):
    sh=wb.worksheets.add(name)
    n=len(headers)
    sh.get_range_by_indexes(0,0,len(rows)+1,n).values=[list(headers)]+[list(r) for r in rows]
    sh.get_range_by_indexes(0,0,1,n).format={'fill':'#17364D','font':{'bold':True,'color':'#FFFFFF'},'row_height':29}
    sh.get_range_by_indexes(1,0,len(rows),n).format.row_height=26
    sh.get_range_by_indexes(1,0,len(rows),n).format.wrap_text=True
    for j,width in enumerate(widths):sh.get_range_by_indexes(0,j,1,1).format.column_width=width
    sh.freeze_panes.freeze_rows(1)
    return sh

add_sheet('v24 Executive Gates', ['Sequence','Workstream','Implemented and tested now','Still missing','Verdict'],[
    [1,'Singapore financial calculations','IRAS resident tax brackets from confirmed chargeable income; CPF OW 2026/27 schedules; CPF static interest Q4 2026; HDB sale waterfall; scenario operators increased to 12','Full CPF account allocation, CPF LIFE premium/payout, multi-year cohort accumulation, complete income tax incl reliefs and tax residency, complex housing, 34 scenario catalogue entries','PARTIAL'],
    [2,'96-persona calibration','All 96 rule definitions, 225 predicate references and uniform weights independently inventoried; structural completeness checked','0 blinded real labels, 0 domain approvals, 0 empirically calibrated scores, 60/70 thresholds unvalidated','NOT CALIBRATED'],
    [3,'Personal-data persistence & consent','Local encrypted synthetic-only SQLite store, separate purposes, adult consent checks, revoke/delete, file permissions','Authenticated identities and multi-tenant isolation, real privacy program, breach response, key rotation, penetration testing, production hosting','PROTOTYPE ONLY'],
    [4,'AI assistant, memory & action tracking','Deterministic guided reply, user-consented encrypted memory, persisted action state machine, no action execution','Live production AI, authenticated access, channels, monitored reminders, real official verification and user UX validation','PARTIAL'],
    [5,'Independent validation','Self-run reproducible numeric/security/consent regression tests and risk register; official source mapping','Independent finance specialist, independent security assessment, Singapore legal advice-perimeter opinion, regulator/authorised-adviser approval as applicable','NOT APPROVED']
], [14,35,94,110,23])

reference=[
    ['FIN-01','IRAS tax','Confirmed chargeable income; YA 2026/27 resident rates','Bounded reference','https://www.iras.gov.sg/taxes/individual-income-tax/basics-of-individual-income-tax/tax-residency-and-tax-rates/individual-income-tax-rates','Cannot infer chargeable income from wages'],
    ['FIN-02','CPF static interest','2026 Q4 unchanged CPF balances; annualised interest illustration','Illustration only','https://www.cpf.gov.sg/service/article/what-are-the-cpf-interest-rates','Real interest calculated monthly; 55+ transitions excluded'],
    ['FIN-03','CPF employee schedule','2026/27 SG and third-year+ PR, OW>750, no AW','Bounded reference','https://www.cpf.gov.sg/employer/employer-obligations/how-much-cpf-contributions-to-pay','No full account allocation, low wage or annual cap'],
    ['FIN-04','HDB sale proceeds','HDB/post-2002 private, official CPF refund and costs supplied','Bounded reference','https://www.cpf.gov.sg/service/article/what-will-happen-to-my-sales-proceeds-after-the-sale-of-my-property','No joint owners / pre-2002, fees/tax or CPF RA handling'],
    ['FIN-05','CPF LIFE payouts','Uses official/user supplied amount; rejects impossible age start','Requires official estimate','https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month','No actuarial payout formula implemented']
]
add_sheet('v24 Financial References',['ID','Module','Supported Inputs','Status','Official source URL','Explicit exclusion'],reference,[15,30,64,22,92,74])

rules=json.loads((ROOT/'audit/score_calibration_review_v24.json').read_text())
score_rows=[]
for p in rules['personas']:
    score_rows.append([p['id'],p['name'],p['gate'],p['exclusion'],' / '.join(map(str,p['weights'])),0,'PENDING','UNVALIDATED','Needs independent human labelling and domain review'])
add_sheet('v24 Score Review',['ID','Archetype','Gate','Exclusion','Weights','Real labelled cases','Domain approval','Status','Action'],score_rows,[13,43,23,25,25,20,20,22,69])

op={
'S001':'job_loss','S002':'job_loss','S003':'job_loss','S004':'job_loss','S007':'commission_drop',
'S008':'job_loss','S009':'commission_drop','S010':'platform_cost_shock','S011':'commission_drop',
'S016':'care_shock','S017':'job_loss','S018':'mortgage_rate_shock','S021':'rent_increase',
'S023':'rental_vacancy','S024':'market_crash','S028':'inflation_shock','S034':'medical_shock',
'S036':'care_shock','S037':'job_loss','S045':'one_time_cost'
}
scenario_records=[]
raw=wb.worksheets.get_item('Life Scenarios').get_range('A2:C55').values
for a,cat,name in raw:
    if not a:continue
    operator=op.get(a,'')
    scenario_records.append([a,cat,name,operator,'BOUNDED OPERATOR / EVENT NOT FULLY MODELLED' if operator else 'NOT IMPLEMENTED',
        'Requires case-specific user inputs and expert review' if operator else 'No tested operator for full financial consequences'])
add_sheet('v24 Scenario Coverage',['ID','Category','Scenario','Existing operator','Status','Critical limitation'],scenario_records,[13,28,37,26,46,71])

risk=[
 ['SEC-01','CRITICAL','No user authentication or multi-tenant authorization','BLOCKED','Never expose beyond localhost / synthetic','Qualified security engineer'],
 ['SEC-02','HIGH','Encryption keys managed via environment only; no rotation/recovery','OPEN','Design KMS/HSM and tested rotation/recovery','Security engineering'],
 ['SEC-03','HIGH','Consent metadata and local audit retained in SQLite','OPEN','Retention, deletion, incident lifecycle design','Privacy counsel and DPO'],
 ['SEC-04','HIGH','Optional LLM adapter could expose user-entered synthetic-labelled text','OPEN','Threat model, redaction, allowlist test, provider DPIA; keep disabled','Security + privacy'],
 ['SEC-05','HIGH','No independent penetration test or infrastructure review','OPEN','Independent pen test and remediation','External assessor'],
 ['FIN-01','CRITICAL','CPF LIFE and full CPF statutory accrual/payout not reconciled','OPEN','Independently reconciled golden cases','CPF financial expert'],
 ['FIN-02','HIGH','Income tax input is chargeable income, not actual taxable earnings','OPEN','Relief/eligibility/tax residency verified module','Tax expert'],
 ['FIN-03','HIGH','Mortgage and property proceeds are bounded only','OPEN','CPF account transitions, accrued refund, owner allocation','Housing/CPF expert'],
 ['PERS-01','HIGH','All 96 weight profiles identical and uncalibrated','OPEN','Blind-labelled independent scenarios and threshold calibration','Product + researchers'],
 ['REG-01','CRITICAL','No legal assessment of FAA advisory perimeter','OPEN','Singapore counsel and regulated-adviser review','External counsel'],
 ['OPS-01','HIGH','No real action verification, reminders or notifications','OPEN','Trusted official integrations and audit','Product engineering'],
 ['UX-01','HIGH','48 planned user interviews have not happened','OPEN','Recruit, run, transcribe and analyse actual study','Research lead']
]
add_sheet('v24 Risk and QA',['Risk ID','Severity','Finding','Status','Closure requirement','Independent reviewer'],risk,[15,16,80,17,83,39])

add_sheet('v24 Test Evidence',['Suite','Command / method','Result','Independence','Meaning'],[
 ['Legacy + new integration','python -m pytest -q','See audit/pytest_v24.txt','Self-run','Structural numerical and local security tests only'],
 ['Original classifier contracts','PYTHONPATH=. python audit/run_rule_contracts_v22.py','See audit/rule_contracts_v24.txt','Self-run','Uncalibrated 96 rules still require human review'],
 ['Local API smoke','python audit/run_api_checks.py','See audit/api_v24.txt','Self-run','Localhost, synthetic-only endpoints'],
 ['Score inventory','python audit/score_audit_v24.py','96 definitions, 225 predicates','Self-run','Not a classification accuracy metric'],
 ['Independent finance','External qualified reviewer','NOT DONE','Not available','Mandatory before external pilot'],
 ['Independent security','External qualified reviewer','NOT DONE','Not available','Mandatory before real customer data'],
 ['Legal/regulatory advice','Singapore counsel / licensed FA','NOT DONE','Not available','Mandatory before regulated recommendations'],
 ['Consumer research','48 stratified interviews planned','0/48','Not available','Cannot claim consumer validation']
], [35,72,39,22,83])

out=ROOT/'RetirePilot_Master_Library_v1.5_Execution_Gates.xlsx'
SpreadsheetFile.export_xlsx(wb).save(str(out))
print('Created:',out)
print('Score rows:',len(score_rows),'Scenarios:',len(scenario_records),'Bounded scenario mappings:',len(op))
