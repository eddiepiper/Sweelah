from artifact_tool import Blob,SpreadsheetFile
from pathlib import Path
import json
src='/mnt/data/RetirePilot_Master_Library_v1.6_Integrity_and_Gates.xlsx'
out=Path(__file__).parent/'data/scenario_contracts_v26.json'
wb=SpreadsheetFile.import_xlsx(Blob.load(src))
library=wb.worksheets.get_item('Life Scenarios').get_range('A2:C47').values
coverage=wb.worksheets.get_item('v24 Scenario Coverage').get_range('A2:D47').values
old={r[0]:r[3] for r in coverage}
# Each row is an explicit *design contract*; a converter only for trivial bounded
# economic subcomponents; none models legal effects, entitlement or actuarial values.
contracts={
 'S005':('RETIREMENT_GOAL_ONLY','new_retirement_age','Only stops primary earned income at a revised retirement age; does not forecast CPF effects.'),
 'S006':('NOT_SAFE_TO_COMPILE','rehiring_offer, effective_date, income, employer CPF','No employment re-entry and statutory contribution recalculation.'),
 'S012':('NOT_SAFE_TO_COMPILE','asset_ownership, consent, legal_settlement, housing, dependants','Divorce settlements, consent and household rights cannot be inferred.'),
 'S013':('NOT_SAFE_TO_COMPILE','survivor_income, insurance, estate, household_consents','Widowhood requires verified survivor and estate changes.'),
 'S014':('RECURRING_COST_COMPONENT','extra_monthly, start_year, duration_years','Cost-only childcare sensitivity; no child benefits, tax relief, insurance or lifecycle modelling.'),
 'S015':('RECURRING_COST_COMPONENT','extra_monthly, start_year, duration_years','Cost-only family-support sensitivity; no tax/transfer eligibility.'),
 'S019':('NOT_SAFE_TO_COMPILE','specific_property_id, valuation, ownership, mortgage','Property valuation affects net worth and LTV, not just cash flow.'),
 'S020':('NOT_SAFE_TO_COMPILE','sale_price, CPF_refund, replacement_home, stamp_duty, moving_cost','Downsizing requires complete property sale and purchase waterfall.'),
 'S022':('NOT_SAFE_TO_COMPILE','HDB_eligibility, lease_age, official_quote, CPF_refund','Lease monetisation requires official HDB eligibility and scheme quote.'),
 'S025':('NOT_SAFE_TO_COMPILE','return_path_by_asset, inflation_path, market_timing','Global lifetime return override would misrepresent bounded low-return years.'),
 'S026':('NOT_SAFE_TO_COMPILE','withdrawal_timing, asset_class_returns, return_sequence','Sequence-of-return risk needs time-indexed portfolio return path.'),
 'S027':('NOT_SAFE_TO_COMPILE','holding_id, holding_value, loss_rate, portfolio_allocation','Current market_crash affects whole portfolio, not specific holdings.'),
 'S029':('RETIREMENT_GOAL_ONLY','new_retirement_age','Stops primary earned income earlier; no automatic CPF/pension/tax recalculation.'),
 'S030':('NOT_SAFE_TO_COMPILE','official_CPF_LIFE_estimate_65_70, start_age','Payout deferral cannot assume universal percent growth or fabricate personal payout.'),
 'S031':('NOT_SAFE_TO_COMPILE','source_account, RA_topup_allowance, verified_cash_availability','CPF RA top-ups require official limits and account transfers.'),
 'S032':('NOT_SAFE_TO_COMPILE','cash_bridge_horizon, essential_expenses, official_payout_start','Bridge funding needs date-aware withdrawal rules and source of cash.'),
 'S033':('NOT_SAFE_TO_COMPILE','affected_CPF_income, contribution_months, residency_cohort','Contribution gaps need future CPF allocation and interest model.'),
 'S035':('RECURRING_COST_COMPONENT','extra_monthly, start_year, duration_years','Disability COST component only; no income disruption, insurance or care eligibility.'),
 'S038':('NOT_SAFE_TO_COMPILE','jurisdiction, residence_status, expenses, taxes, FX, healthcare','Foreign retirement requires jurisdiction-specific tax, healthcare and residency model.'),
 'S039':('NOT_SAFE_TO_COMPILE','currency, FX_path, foreign_assets, liabilities','FX shock needs explicit currency amounts and dated rates.'),
 'S040':('NOT_SAFE_TO_COMPILE','residence_history, relocation_costs, tax_domicile, FX','Repatriation needs cross-border law and verified flows.'),
 'S041':('NOT_SAFE_TO_COMPILE','foreign_pension_currency, indexation, source, taxes','Foreign pension changes need verified terms and FX/tax handling.'),
 'S042':('NET_CASH_RECEIPT_COMPONENT','net_received_once, start_year','Confirmed NET cash receipt only, no estate entitlement/probate/tax prediction.'),
 'S043':('NOT_SAFE_TO_COMPILE','sale_net, liabilities, owner_shares, future_business_income','Business disposal requires cap gains/tax, liabilities and earnings cessation.'),
 'S044':('NET_CASH_GIFT_COMPONENT','net_cash_gift_once, start_year','Cash gift only; cannot assess CPF eligibility, gift tax overseas or heirs rights.'),
 'S046':('NOT_SAFE_TO_COMPILE','business_debt, liability_guarantees, income_history, personal_exposure','Business failure affects liabilities, income, ownership and guarantees together.'),
}
missing=[s for s in [r[0] for r in library] if not old[s]]
assert set(missing)==set(contracts),(missing,set(contracts))
records=[]
for sid,cat,name in library:
    if sid in contracts:
        strategy,required,lim=contracts[sid]
        records.append({'id':sid,'category':cat,'name':name,'previous_status':'UNMAPPED',
            'execution_strategy':strategy,'design_status':'MAPPED_TO_EXPLICIT_CONTRACT_NOT_PRODUCTION_READY',
            'required_inputs':required.split(', '),'blocking_gap':lim,'limitations':[lim,'All values must be verified/user-supplied; synthetic only'],
            'implemented_component':strategy!='NOT_SAFE_TO_COMPILE'})
    else:
        records.append({'id':sid,'category':cat,'name':name,'previous_status':'BOUNDED_OPERATOR',
            'execution_strategy':'NOT_SAFE_TO_COMPILE','existing_operator':old[sid],
            'design_status':'PREEXISTING_BOUNDED_MAPPING_NOT_FULL_EVENT',
            'required_inputs':['reference current v2.5 bounded operator contract'],
            'blocking_gap':'Existing operator is not a full life event; use API operator directly with scenario safeguards.',
            'limitations':['Original mapping may cover only a cash-flow component'], 'implemented_component':False})
assert len(records)==46
out.write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
print({'catalogue':len(records),'previously_unmapped':len(missing),'new_component_converters':sum(x['implemented_component'] for x in records),'blocked_new_contracts':sum(x['previous_status']=='UNMAPPED' and not x['implemented_component'] for x in records)})
