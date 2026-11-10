#!/usr/bin/env python3
"""Build data/scenario_mapping_internal_issue8.json (SWEELAH-ISSUE-8, Refs #8).

INTERNAL / UNVALIDATED. Engineering's in-house mapping of the 26 catalogue
entries that v2.5 left unmapped. Semantic scope, engines, required facts and
guardrails are copied from the repo's synthetic research contracts
(research/retirepilot_2026_11_04/scenario_engine_contracts_46.json); runtime
level is read from the v2.6 registry and the v2.7 priority previews; timing,
missing-data, incompatibility and rationale fields are Engineering's own
judgement. Synthetic/public inputs only; nothing here is externally reviewed.

Deterministic: re-running produces byte-identical output.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from retirepilot.priority_scenarios_v27 import PRIORITY_STATUS  # noqa: E402

RESEARCH = ROOT / 'research/retirepilot_2026_11_04'
OUT = ROOT / 'data/scenario_mapping_internal_issue8.json'
V26 = 'tests/test_cpf_and_scenario_contracts_v26.py'
V27 = 'tests/test_approved_decisions_v27.py'
FAIL_CLOSED_TEST = f'{V26}::test_unimplemented_events_do_not_silently_run'

# Engineering-authored fields: (timing_rule, missing_data_behaviour, incompatible_with, extra_tests, rationale)
REQUIRE = 'Refuse (fail closed) until every required fact is user-supplied or member-transcribed from an official source; unknown is never zero.'
AUTHORED = {
 'S005': ('New retirement age must exceed the approved age; change applies from the month after the original stop-work month.',
          'Refuse without new_retirement_age and an existing approved retirement age.', ['S029'],
          [f'{V26}::test_retirement_target_recalculated_only_by_explicit_input'],
          'Existing RETIREMENT_GOAL_ONLY converter moves the stop-work age only; full mapping adds F03/F06 CPF accrual, which is not implemented, so coverage stays a limited component.'),
 'S006': ('Job stream starts on the verified effective_date (>= as_of) and only after the household member has stopped work.',
          REQUIRE, ['S033', 'S046'], [],
          'Needs a new dated income stream plus employee/SEP/platform CPF recalculation (F03-F05); no safe component subset exists, so it stays fail-closed.'),
 'S012': ('Effects start only from a documented separation/settlement date; nothing is back-dated.',
          'Block: never infer property division, maintenance, CPF or custody without actual terms.', ['S013'],
          [f'{V27}::test_divorce_requires_legal_and_consent_inputs_not_formula', f'{V27}::test_all_five_priorities_have_explicit_contract'],
          'Priority 5A item whose v2.7 entry deliberately always blocks; mapping to F01/F12/F18 records the facts a future engine needs without implying any effect.'),
 'S013': ('Applies from a verified date of death; survivor receipts start only on confirmed payment dates.',
          'Block: do not assume insurance, estate or survivor CPF payments.', ['S012'], [],
          'Requires verified survivor income, claims and estate data across F07/F11/F18; nothing can be computed from defaults, so fail-closed.'),
 'S014': ('start_year >= as_of year; duration_years 1-50; cost applies monthly within that window.',
          'Refuse without a positive user-supplied extra_monthly.', [], [f'{V26}::test_cost_subcomponent_requires_user_value'],
          'Cost-only recurring component already exists; benefits/grants (F17) stay excluded from baseline per D12, so it remains a limited component.'),
 'S015': ('start_year >= as_of year; duration_years 1-50; one-time vs recurring must be chosen explicitly.',
          'Refuse without a positive user-supplied extra_monthly.', ['S044'], [f'{V26}::test_cost_subcomponent_requires_user_value'],
          'Recurring-cost component covers cash support; incompatible with S044 for the same transfer to avoid double counting (D16).'),
 'S019': ('Revaluation dated at a user-supplied valuation date; no cash flow is created.',
          REQUIRE, ['S020', 'S022'], [],
          'A net-worth/LTV change, not a cash outflow; the current projection has no per-property equity ledger (F08), so it fails closed.'),
 'S020': ('Sale completion date and replacement purchase date must both be supplied; CPF refund is credited at completion, not as spendable cash.',
          'Refuse without member-transcribed official CPF property refund; show deficit rather than affordability when financing is needed (D11).', ['S019', 'S022'],
          [f'{V27}::test_downsize_requires_official_cpf_refund'],
          'Priority 5A item with a v2.7 cash-arithmetic preview that may not post to the projection; the full F08/F06 waterfall is not implemented.'),
 'S022': ('Receipts dated from an official scheme quote; lease and RA effects follow the quoted dates only.',
          REQUIRE, ['S020', 'S019'], [],
          'Depends on official HDB eligibility and quote; no estimate is permitted, so it fails closed.'),
 'S025': ('Explicit per-year nominal return and inflation paths; each year applied once.',
          REQUIRE, ['S024', 'S026', 'S028'], [],
          'Needs per-asset return and inflation paths (F10); a global override would double-subtract inflation alongside S028, so it fails closed.'),
 'S026': ('Ordered, dated return path applied before/after each withdrawal consistently.',
          REQUIRE, ['S024', 'S025'], [],
          'Sequence-of-returns risk requires a time-indexed portfolio path (F10/F14) that does not exist yet; fail-closed.'),
 'S027': ('Shock dated to a single holding at a user-supplied date.',
          REQUIRE, ['S024'], [],
          'Needs holding-level portfolio detail; reusing market_crash would wrongly shock the whole portfolio, so it fails closed.'),
 'S029': ('New retirement age must be below the approved age; CPF LIFE start age is not moved.',
          'Refuse without new_retirement_age and an existing approved retirement age.', ['S005'],
          [f'{V26}::test_retirement_target_recalculated_only_by_explicit_input', f'{V26}::test_incomplete_retirement_scenario_blocked'],
          'Existing converter moves the stop-work age only; liquidity bridge (F14) and CPF effects (F03/F06/F07) are not implemented, so limited component.'),
 'S030': ('Compare two member-transcribed official estimates dated with their as-of date; no break-even.',
          'Refuse unless estimate_source is a member-transcribed official CPF estimate (D-002).', ['S032'],
          [f'{V27}::test_payout_timing_never_infers_cpf_amounts'],
          'Priority 5A item with a v2.7 comparison-only preview; no actuarial or lifetime calculation, so limited preview.'),
 'S031': ('Top-up dated at transfer; payout change only from a new official member estimate.',
          REQUIRE, [], [],
          'Needs verified RA limits and account transfers on the F06 ledger plus a fresh F07 estimate; fail-closed.'),
 'S032': ('Bridge runs from stop-work date to the member-provided official payout start date.',
          REQUIRE, ['S030'], [],
          'Needs dated cash drawdown and reserve logic (F14, D09); restricted CPF can never fill the gap, so fail-closed until built.'),
 'S033': ('Suspends contributions only for the verified months of the affected income stream.',
          REQUIRE, ['S006'], [],
          'Needs contributor-specific CPF posting and allocation (F03-F06); never assume contributions continue, so fail-closed.'),
 'S035': ('start_year >= as_of year; duration_years 1-50; cost applies monthly within that window.',
          'Refuse without a positive user-supplied extra_monthly.', ['S036'], [f'{V26}::test_cost_subcomponent_requires_user_value'],
          'Cost component exists; income disruption (F02) and benefits (F11/F17) are separate and unimplemented; overlapping S036 care cost would double count.'),
 'S038': ('Relocation dated from a user-supplied move date; jurisdiction rules apply only from then.',
          'Block jurisdiction-specific rules that are not sourced (D13).', ['S040'], [],
          'Cross-border tax, healthcare, residency and FX (F09/F13/F15) are unsupported, so fail-closed.'),
 'S039': ('Each foreign exposure revalued on a dated FX path; unrealised changes are not cash.',
          REQUIRE, [], [],
          'Needs explicit currency amounts and dated FX rates (F15); fail-closed.'),
 'S040': ('Offshore streams end and onshore streams start on a documented return date.',
          'Block until residency and tax effects are documented (D13).', ['S038'], [],
          'Cross-border law and verified flows required; fail-closed.'),
 'S041': ('Change applies from the pension provider\'s documented effective date.',
          'Block: no unverified foreign pension entitlement (D13).', [], [],
          'Needs verified foreign pension terms with FX and withholding (F13/F15); fail-closed.'),
 'S042': ('Posted once in start_year after probate and actual transfer; pending estate is not cash.',
          'Refuse without a positive confirmed net_received_once; excluded from baseline (D12).', [],
          [f'{V26}::test_inheritance_only_user_confirmed_net_cash_receipt'],
          'Net cash receipt component exists; entitlement, probate and tax are out of scope, so limited component.'),
 'S043': ('Proceeds booked at verified completion; business income and equity stop the same date.',
          REQUIRE, ['S046'], [],
          'Needs net proceeds, liabilities and earnings cessation (F02/F09/F18); avoid double counting value and proceeds, so fail-closed.'),
 'S044': ('Posted once in start_year from liquid assets; restricted CPF can never be gifted.',
          'Refuse without a positive net_cash_gift_once.', ['S015'], [f'{V26}::test_gift_depletes_cash_and_is_not_tax_eligibility'],
          'Cash gift outflow component exists; recipient-household effects only when ownership is known, so limited component.'),
 'S046': ('Revenue stops at a documented closure date; personal exposure only for documented guarantees.',
          'Block: company debt is never automatically transferred to the individual.', ['S043', 'S006'], [],
          'Liabilities, guarantees and income must be documented together (F02/F18); fail-closed.'),
}


def _decisions(sid, engines, decisions):
    out = []
    for d in decisions:
        tokens = {t.strip() for t in d['Affected engines'].replace(',', '/').split('/')}
        if 'All scenarios' in tokens or sid in tokens or tokens & set(engines):
            # D11 names F08 only in the context of downsizing (S020); keep it scoped there.
            if d['ID'] == 'D11' and sid != 'S020':
                continue
            out.append(d['ID'])
    return out


def build():
    reg = {r['id']: r for r in json.loads((ROOT / 'data/scenario_contracts_v26.json').read_text())}
    spec = {s['ID']: s for s in json.loads((RESEARCH / 'scenario_engine_contracts_46.json').read_text())}
    decisions = json.loads((RESEARCH / 'APPROVED_PRODUCT_DECISIONS_D08_D16.json').read_text())
    unmapped = sorted(s for s, r in reg.items() if r['previous_status'] == 'UNMAPPED')
    assert len(unmapped) == 26 and set(unmapped) == set(AUTHORED), unmapped
    entries = []
    for sid in unmapped:
        r, s = reg[sid], spec[sid]
        timing, missing, incompat, extra_tests, rationale = AUTHORED[sid]
        engines = s['Financial engines'].split(',')
        if sid in PRIORITY_STATUS:
            level = 'BLOCKED_PREVIEW' if PRIORITY_STATUS[sid][1].startswith('BLOCKED') else 'LIMITED_PREVIEW'
        elif r['implemented_component']:
            level = 'LIMITED_COMPONENT'
        else:
            level = 'NOT_IMPLEMENTED_FAIL_CLOSED'
        tests = list(extra_tests)
        if r['execution_strategy'] == 'NOT_SAFE_TO_COMPILE':
            tests.append(FAIL_CLOSED_TEST)
        entries.append({
            'id': sid, 'v26_name': r['name'], 'v26_category': r['category'],
            'v26_execution_strategy': r['execution_strategy'],
            'v27_priority_preview': sid if sid in PRIORITY_STATUS else None,
            'previous_status': 'UNMAPPED', 'mapping_status': 'MAPPED_INTERNAL',
            'validation_status': 'INTERNAL_UNVALIDATED', 'external_validation': False,
            'mapped_by': 'Engineering Lead (in-house)',
            'semantic_scope': s['Event and calculation rule'],
            'financial_engines': engines,
            'required_facts': [x.strip() for x in s['Required facts'].split(';')],
            'guardrail': s['Guardrail / refusal'],
            'timing_rule': timing, 'missing_data_behaviour': missing,
            'incompatible_with': incompat,
            'applicable_decisions': _decisions(sid, engines, decisions),
            'coverage': {'mapped': True, 'implemented': level, 'golden_tested': False, 'domain_approved': False},
            'component_tests': tests,
            'rationale': rationale,
        })
    doc = {
        'schema': 'sweelah.scenario_mapping_internal/1',
        'task': 'SWEELAH-ISSUE-8', 'issue': 'eddiepiper/Sweelah#8', 'as_of': '2026-11-10',
        'validation_status': 'INTERNAL_UNVALIDATED', 'external_validation': False, 'synthetic_only': True,
        'phase_9': 'NO_GO',
        'label': ('INTERNAL / UNVALIDATED. In-house engineering mapping, not externally validated, '
                  'not domain-reviewed, no sign-off. Mapped does not mean implemented, golden-tested '
                  'or approved; unsupported entries still fail closed and imply no effect.'),
        'coverage_levels': {
            'mapped': 'Engineering has recorded scope, engines, facts, guardrail, timing and conflicts.',
            'implemented': 'Runtime level: LIMITED_COMPONENT (v2.6 converter), LIMITED_PREVIEW / BLOCKED_PREVIEW (v2.7), or NOT_IMPLEMENTED_FAIL_CLOSED.',
            'golden_tested': 'Independent golden reference for the full event semantics. None exist.',
            'domain_approved': 'Qualified external domain review. None exist.'},
        'sources': ['data/scenario_contracts_v26.json',
                    'research/retirepilot_2026_11_04/scenario_engine_contracts_46.json',
                    'research/retirepilot_2026_11_04/financial_engine_contracts_18.json',
                    'research/retirepilot_2026_11_04/APPROVED_PRODUCT_DECISIONS_D08_D16.json',
                    'retirepilot/priority_scenarios_v27.py'],
        'entries': entries,
    }
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print({'entries': len(entries), 'levels': {l: sum(e['coverage']['implemented'] == l for e in entries)
           for l in sorted({e['coverage']['implemented'] for e in entries})}})


if __name__ == '__main__':
    build()
