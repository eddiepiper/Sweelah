#!/usr/bin/env python3
"""Build data/persona_draft_labels_issue3.json (SWEELAH-ISSUE-3, Refs #3).

INTERNAL DRAFT. Product-owned first pass, pending Head of Product review.
Not independently reviewed. Labels are derived from existing fields in
retirepilot/retirepilot_rules_v1.2.json (gate, criteria, name, family,
planning_focus). Taxonomy source: Head of Product specification,
Status: Proposed. Aligns with PSD v2.7 section 3 and Appendix A, and
with docs/APPROVED_DECISIONS_v2.7.md decisions 1A, 2A, 3A and 7A.

Decision 1A: no risk tier; these labels are not suitability advice.
Decision 2A: cpf_retirement_situation values describe patterns only;
no amounts and no entitlement claims.
Decision 3A: internal only; not for the consumer UI, API or exports
until reviewed; matching gates, weights and results are unchanged.
Decision 7A: evidence_level is JSON null (internal design, no research).

Where an age band, work type, CPF situation or household context is
not clearly stated, the first pass uses varies or spans_stages rather
than guessing. Synthetic / public fields only. Phase 9 stays NO-GO.

Deterministic: re-running produces byte-identical output.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "retirepilot/retirepilot_rules_v1.2.json"
DEFAULT_OUT = ROOT / "data/persona_draft_labels_issue3.json"
DRAFT_STATUS = "DRAFT_NOT_INDEPENDENTLY_REVIEWED"
# Decision 7A: no evidence yet. Serialised as JSON null (QA G5 on 8e812e0 found
# the string "None" here, a str(None)-style leak; it was never an enum value).
EVIDENCE_NONE = None

# Each row: persona_id, life_stage, work_income_type, cpf_retirement_situation,
# household_context, planning_complexity, planning_complexity_reason, rationale_note.
# planning_complexity_reason is INTERNAL ONLY (decision 3A). Phrases such as
# "specialist review" and L08 "protective referral" must never appear in the
# consumer UI, API, exports or the assistant.
ROWS = [
    ('A01', 'spans_stages', 'salaried', 'accumulating', 'varies', 'elevated',
     'Low income with high essential costs and low liquidity raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate employee maps to salaried; cpf_contrib indicates accumulating; no household predicate, so household_context is varies.'),
    ('A02', 'spans_stages', 'salaried', 'accumulating', 'dependants', 'standard',
     'Typical salaried household planning around housing and dependants.',
     'No age-band predicate, so life_stage is spans_stages; gate employee maps to salaried; cpf_contrib indicates accumulating; children_dependent maps to dependants.'),
    ('A03', 'spans_stages', 'salaried', 'varies', 'varies', 'standard',
     'High income with investment assets and a retirement goal, and no constraint predicate, is a standard planning situation, on the same footing as H02.',
     'No age-band predicate, so life_stage is spans_stages; gate employee maps to salaried; no CPF-retirement predicate, so cpf_retirement_situation is varies; no household predicate, so household_context is varies.'),
    ('A04', 'spans_stages', 'salaried', 'varies', 'couple', 'standard',
     'Joint dual-earner planning with no constraint predicate is a standard planning situation, on the same footing as D01.',
     'No age-band predicate, so life_stage is spans_stages; criteria employee maps to salaried; no CPF-retirement predicate, so cpf_retirement_situation is varies; household_dual_earner and partner_earns map to couple.'),
    ('A05', 'spans_stages', 'salaried', 'varies', 'dependants', 'elevated',
     'Household dependence on one salary raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; criteria employee maps to salaried; no CPF-retirement predicate, so cpf_retirement_situation is varies; children_dependent and high_dependency map to dependants rather than couple.'),
    ('A06', 'spans_stages', 'salaried', 'accumulating', 'varies', 'elevated',
     'Contract renewal uncertainty and contribution gaps raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; criteria employee and gate contract_work map to salaried; a contribution pathway with gaps, cited in the planning_focus, maps to accumulating as a pattern, not an entitlement.'),
    ('A07', 'spans_stages', 'not_working', 'varies', 'varies', 'elevated',
     'Income interruption after retrenchment raises planning difficulty.',
     'late_career is not a tight age band, so life_stage is spans_stages; gate retrenchment_event with previously_employee and income_interrupted, and no new work predicate, maps to not_working; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('A08', 'spans_stages', 'salaried', 'payout_started', 'varies', 'elevated',
     'Working later than a typical retirement goal raises timing difficulty.',
     'age_60plus and working_beyond_65 span more than one life-stage band, so life_stage is spans_stages; gate employee maps to salaried; cpf_income maps to payout_started as a pattern, not an entitlement, consistent with B08, G08, I07, L03 and L04; current work is recorded separately in work_income_type and does not negate a payout pattern.'),
    ('B01', 'spans_stages', 'platform_gig', 'accumulating', 'varies', 'elevated',
     'Platform earnings, vehicle costs and a CPF opt-in path raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate ridehail_platform maps to platform_gig; platform_opted_in and cpf_platform indicate accumulating; no household predicate, so household_context is varies.'),
    ('B02', 'spans_stages', 'platform_gig', 'limited_or_no_cpf', 'varies', 'elevated',
     'Platform earnings without a CPF opt-in, using a MediSave path, raise planning difficulty.',
     'age_45plus is open-ended rather than a single band, so life_stage is spans_stages; gate ridehail_platform maps to platform_gig; platform_not_opted_in and medisave_path map to limited_or_no_cpf as a pattern, not an entitlement.'),
    ('B03', 'spans_stages', 'platform_gig', 'varies', 'varies', 'elevated',
     'Operating costs, injury exposure and earnings volatility raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate delivery_motorcycle maps to platform_gig; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('B04', 'spans_stages', 'platform_gig', 'varies', 'varies', 'elevated',
     'Physically demanding platform work with irregular earnings raises planning difficulty.',
     'age_60plus spans more than one life-stage band, so life_stage is spans_stages; gate delivery_nonmotor maps to platform_gig; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('B05', 'spans_stages', 'platform_gig', 'varies', 'varies', 'elevated',
     'Consolidating income across platforms raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate multiple_platforms maps to platform_gig; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('B06', 'spans_stages', 'mixed', 'accumulating', 'varies', 'elevated',
     'Salary and platform side income follow separate contribution pathways.',
     'No age-band predicate, so life_stage is spans_stages; salary_income plus platform_side_income maps to mixed; separate_contribution indicates accumulating; no household predicate, so household_context is varies.'),
    ('B07', 'spans_stages', 'platform_gig', 'varies', 'varies', 'elevated',
     'Replacement gig earnings after retrenchment raise retirement-gap difficulty.',
     'late_career is not a tight age band, so life_stage is spans_stages; current platform_income after retrenchment_event maps to platform_gig; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('B08', 'payout_age_65_plus', 'platform_gig', 'payout_started', 'varies', 'elevated',
     'Older platform driving with reduced hours and payouts raises planning difficulty.',
     'Criteria age_65plus maps to payout_age_65_plus; gate driver_taxi_phv maps to platform_gig; age_65plus with cpf_income maps to payout_started as a pattern; no household predicate, so household_context is varies.'),
    ('C01', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'elevated',
     'Irregular commissions and thin cash reserves raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate property_agent and commission_income map to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('C02', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'elevated',
     'Multi-year commission volatility, tax and savings raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate property_agent and commission_income map to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('C03', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'elevated',
     'Declining commissions near a retirement goal raise timing difficulty.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; gate property_agent maps to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('C04', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'elevated',
     'Commission persistence and volatility raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate insurance_agent and commission_income map to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('C05', 'spans_stages', 'self_employed_or_commission', 'limited_or_no_cpf', 'varies', 'elevated',
     'Contract gaps and SEP MediSave contributions raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate freelance_professional maps to self_employed_or_commission; sep_medisave maps to limited_or_no_cpf as a MediSave-only pattern, not an entitlement.'),
    ('C06', 'spans_stages', 'self_employed_or_commission', 'limited_or_no_cpf', 'varies', 'elevated',
     'Business costs, thin liquidity and SEP MediSave raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate hawker_or_sole_prop maps to self_employed_or_commission; sep_medisave maps to limited_or_no_cpf as a MediSave-only pattern, not an entitlement.'),
    ('C07', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'specialist_review_suggested',
     'Business equity, succession and exit planning suggest specialist review.',
     'No age-band predicate, so life_stage is spans_stages; gate sme_owner maps to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('C08', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'elevated',
     'Integrating business, rent and investment income raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate entrepreneur and multiple_income_types map to self_employed_or_commission as the organising work pattern; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('D01', 'spans_stages', 'not_applicable', 'varies', 'couple', 'standard',
     'Joint retirement objectives for a couple without children are a standard planning situation.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies; married household_dual_earner with no_children maps to couple.'),
    ('D02', 'spans_stages', 'not_applicable', 'varies', 'single', 'standard',
     'Solo retirement and housing security for a single household is a standard planning situation.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies; single_household and never_married map to single.'),
    ('D03', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'standard',
     'Education and household obligations for parents with children are a standard planning situation.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies; household_with_children maps to dependants.'),
    ('D04', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'elevated',
     'Childcare, protection and savings in a one-parent household raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; children_dependent and one_parent_household map to dependants rather than single, because child obligations organise the pattern.'),
    ('D05', 'spans_stages', 'not_applicable', 'varies', 'caregiver', 'elevated',
     'Supporting children and an ageing parent at the same time raises planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; parent_supported and care_expenses map to caregiver rather than dependants, because sandwiched care organises the pattern.'),
    ('D06', 'spans_stages', 'not_working', 'limited_or_no_cpf', 'couple', 'elevated',
     'Individual retirement adequacy with spousal income dependence raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate individual_not_earning maps to not_working; personal_cpf_low maps to limited_or_no_cpf as a pattern, not an entitlement; married and partner_earns map to couple.'),
    ('D07', 'spans_stages', 'not_applicable', 'varies', 'multi_generation', 'elevated',
     'Shared expenses and cross-generation support raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; gate multigenerational_household maps to multi_generation.'),
    ('D08', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'elevated',
     'Continued transfers to adult children raise retirement affordability difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; adult_child_supported and parent_of_adult map to dependants.'),
    ('E01', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'specialist_review_suggested',
     'Asset division, housing transition and child obligations after divorce suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; children_dependent and child_support map to dependants.'),
    ('E02', 'near_retirement_55_64', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'CPF and capital after a divorce settlement near retirement suggest specialist review.',
     "Name 'Divorced pre-retiree' plus age_55plus and retirement_soon map to near_retirement_55_64; work type is not stated, so work_income_type is not_applicable; cpf_settlement is not a tight CPF-retirement pattern, so cpf_retirement_situation is varies; post-divorce household context is not stated, so household_context is varies."),
    ('E03', 'spans_stages', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'Lost household income, estate proceeds and insurance claims after widowhood suggest specialist review.',
     'No age-band predicate, so life_stage is spans_stages; the name says working adult but no work-type predicate is present, so work_income_type is not_applicable; no CPF-retirement or current household-structure predicate, so those fields vary.'),
    ('E04', 'spans_stages', 'not_working', 'varies', 'single', 'elevated',
     'Survivor income and revised spending after widowhood in retirement raise planning difficulty.',
     'retired_status without an age-band predicate is not enough to choose a life-stage band, so life_stage is spans_stages; retired_status maps to not_working; no CPF-retirement predicate, so cpf_retirement_situation is varies; living_alone maps to single.'),
    ('E05', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'specialist_review_suggested',
     'Blended-family dependants and beneficiary planning suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; blended_family and previous_dependants map to dependants.'),
    ('E06', 'spans_stages', 'not_applicable', 'varies', 'couple', 'specialist_review_suggested',
     'Separate assets, property rights and estate plans for unmarried partners suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; gate cohabiting_unmarried with partner_earns maps to couple.'),
    ('E07', 'spans_stages', 'not_applicable', 'varies', 'single', 'elevated',
     'Retirement without expected family support raises planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; single_household and no_family_support map to single.'),
    ('E08', 'spans_stages', 'not_applicable', 'varies', 'caregiver', 'specialist_review_suggested',
     "Financial authority, capacity and safeguarding when managing a parent's finances suggest specialist review.",
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; manages_parent_finances, parent_supported and safeguarding_needed map to caregiver.'),
    ('F01', 'spans_stages', 'not_applicable', 'varies', 'varies', 'standard',
     'Housing security with a fully paid HDB flat is a standard planning situation.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; cpf_housing_use is a housing-use pattern, not a retirement-situation pattern, so cpf_retirement_situation is varies; no household predicate, so household_context is varies.'),
    ('F02', 'spans_stages', 'not_applicable', 'varies', 'varies', 'standard',
     'Servicing an HDB mortgage alongside a retirement goal is a standard planning situation.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; no work-type predicate, so work_income_type is not_applicable; cpf_housing_use is not a retirement-situation pattern, so cpf_retirement_situation is varies.'),
    ('F03', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Private-property concentration with an active mortgage raises planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('F04', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Rental yields, vacancy and tax across multiple properties raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; rental_income is asset income, not a work type; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('F05', 'payout_age_65_plus', 'not_applicable', 'varies', 'varies', 'elevated',
     'An asset-rich, cash-poor senior homeowner faces monetisation and liquidity difficulty.',
     'Gate age_65plus maps to payout_age_65_plus; no work-type predicate, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('F06', 'payout_age_65_plus', 'not_working', 'varies', 'varies', 'elevated',
     'Long-term rental affordability in retirement raises planning difficulty.',
     'Criteria age_65plus maps to payout_age_65_plus; retired_status maps to not_working; no CPF-retirement predicate, so cpf_retirement_situation is varies; no household predicate, so household_context is varies.'),
    ('F07', 'payout_age_65_plus', 'not_applicable', 'varies', 'multi_generation', 'elevated',
     'Housing dependency on adult children and contingency planning raise difficulty.',
     'Gate age_65plus maps to payout_age_65_plus; no work-type or retired_status predicate, so work_income_type is not_applicable; living_with_adult_child maps to multi_generation.'),
    ('F08', 'payout_age_65_plus', 'not_applicable', 'varies', 'varies', 'elevated',
     'Downsizing or lease buyback proceeds and scheme eligibility raise planning difficulty.',
     'Criteria age_65plus maps to payout_age_65_plus; no work-type predicate, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('G01', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Funding retirement before CPF payout age raises a pre-payout bridge difficulty.',
     'age_under_65 and pre_65_bridge cover more than one life-stage band, so life_stage is spans_stages; work type is not stated, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('G02', 'spans_stages', 'not_working', 'varies', 'varies', 'elevated',
     'Investment withdrawal sustainability for an early retiree raises planning difficulty.',
     'age_under_65 covers more than one life-stage band, so life_stage is spans_stages; gate early_retired maps to not_working; payout is not stated, so cpf_retirement_situation is varies.'),
    ('G03', 'spans_stages', 'not_applicable', 'limited_or_no_cpf', 'varies', 'elevated',
     'A retirement funding-gap with low CPF and low liquidity raises planning difficulty.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; work type is not stated, so work_income_type is not_applicable; cpf_low maps to limited_or_no_cpf as a pattern, not an entitlement.'),
    ('G04', 'near_retirement_55_64', 'not_working', 'payout_deferred', 'varies', 'elevated',
     'A pre-payout income bridge after stopping work at the stated retirement age raises difficulty.',
     'Gate retire_at_60 with age_60plus and pre_65_bridge maps to near_retirement_55_64; income_interrupted maps to not_working; cpf_payout_deferred maps to payout_deferred; no household predicate, so household_context is varies.'),
    ('G05', 'payout_age_65_plus', 'not_working', 'payout_started', 'varies', 'elevated',
     'CPF LIFE payout choices and household income at commencement raise planning difficulty.',
     'Criteria age_65plus and gate cpf_life_starting map to payout_age_65_plus; retired_status maps to not_working; cpf_life_starting with cpf_income maps to payout_started as a pattern, not an entitlement.'),
    ('G06', 'payout_age_65_plus', 'not_working', 'payout_deferred', 'varies', 'elevated',
     'An income bridge while considering payout deferral raises planning difficulty.',
     'Criteria age_65plus maps to payout_age_65_plus; the name is a retiree with no work predicate, so work_income_type is not_working; gate cpf_payout_deferred maps to payout_deferred.'),
    ('G07', 'payout_age_65_plus', 'mixed', 'varies', 'varies', 'elevated',
     'Part-time consulting combined with staged withdrawals raises planning difficulty.',
     'Criteria age_65plus maps to payout_age_65_plus; parttime_work and consulting_income plus withdrawal_income map to mixed; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('G08', 'payout_age_65_plus', 'not_working', 'payout_started', 'varies', 'elevated',
     'Longevity and ongoing care expenditure in later retirement raise planning difficulty.',
     'Gate age_80plus maps to payout_age_65_plus; retired_status maps to not_working; cpf_income with retired_status maps to payout_started as a pattern, not an entitlement.'),
    ('H01', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'High earnings with low savings and high spending raise accumulation difficulty.',
     'No age-band predicate, so life_stage is spans_stages; income_high does not state a work type, so work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('H02', 'spans_stages', 'not_applicable', 'varies', 'varies', 'standard',
     'Asset-supported flexibility for a moderate earner is a standard planning situation.',
     'No age-band predicate, so life_stage is spans_stages; income_mid does not state a work type, so work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('H03', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'High CPF balances with low accessible cash raise liquidity difficulty.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; no work-type predicate, so work_income_type is not_applicable; cpf_high and cpf_housing_use are stock or housing-use patterns, not a tight retirement situation, so cpf_retirement_situation is varies.'),
    ('H04', 'spans_stages', 'not_working', 'varies', 'varies', 'elevated',
     'Market and withdrawal sequencing for an investment-funded retiree raise planning difficulty.',
     'The name is a retiree but no age-band predicate is present, so life_stage is spans_stages; investment_funded_retirement and withdrawal_income map to not_working; limited_guaranteed_income is not a tight CPF pattern, so cpf_retirement_situation is varies.'),
    ('H05', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Property concentration and illiquidity raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('H06', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'High debt service against high income with low liquidity raises affordability difficulty.',
     'No age-band predicate, so life_stage is spans_stages; income_high does not state a work type, so work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('H07', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Single-asset equity exposure and diversification needs raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; employer_shares do not confirm current work type, so work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('H08', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Windfall management and future cash flow after an inheritance raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('I01', 'spans_stages', 'salaried', 'varies', 'varies', 'elevated',
     'Recurring medical costs alongside employment raise continuity difficulty.',
     'No age-band predicate, so life_stage is spans_stages; criteria employee maps to salaried; no CPF-retirement or household predicate, so those fields vary.'),
    ('I02', 'spans_stages', 'salaried', 'varies', 'varies', 'elevated',
     'Disability-related costs and variable work capacity raise employment-sustainability difficulty.',
     'No age-band predicate, so life_stage is spans_stages; criteria employee maps to salaried; no CPF-retirement or household predicate, so those fields vary.'),
    ('I03', 'spans_stages', 'not_working', 'varies', 'varies', 'elevated',
     'Income replacement and support after being unable to continue working raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate unable_to_work and income_interrupted map to not_working; support_eligibility is not a CPF-retirement pattern, so cpf_retirement_situation is varies.'),
    ('I04', 'spans_stages', 'not_applicable', 'varies', 'caregiver', 'specialist_review_suggested',
     'Lifetime dependency and succession for an adult with a lifelong disability suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; parent_of_adult with care_expenses and high_dependency map to caregiver rather than dependants, because lifelong care organises the pattern.'),
    ('I05', 'spans_stages', 'not_working', 'limited_or_no_cpf', 'caregiver', 'elevated',
     'Lost salary and thinner CPF accumulation after leaving work to give care raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate caregiver_left_work and income_interrupted map to not_working; personal_cpf_low maps to limited_or_no_cpf as a pattern, not an entitlement; parent_supported and care_expenses map to caregiver.'),
    ('I06', 'payout_age_65_plus', 'not_applicable', 'varies', 'varies', 'elevated',
     'Long-term care financing for a senior with growing care needs raises planning difficulty.',
     'Gate age_65plus maps to payout_age_65_plus; no work-type or retired_status predicate, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('I07', 'spans_stages', 'not_working', 'payout_started', 'varies', 'elevated',
     'Recurring medication costs in retirement raise planning difficulty.',
     'retired_status without an age-band predicate is not enough to choose a life-stage band, so life_stage is spans_stages; retired_status maps to not_working; cpf_income with retired_status maps to payout_started as a pattern, not an entitlement.'),
    ('I08', 'spans_stages', 'not_applicable', 'varies', 'caregiver', 'specialist_review_suggested',
     'Funding residential care and a second household expense set suggests specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; partner_residential_care and care_expenses map to caregiver rather than couple, because care funding organises the pattern.'),
    ('J01', 'spans_stages', 'salaried', 'varies', 'varies', 'elevated',
     'Low wages, essential expenses and low liquidity raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate employee maps to salaried; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('J02', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Irregular hours and inadequate earnings raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; underemployed and hours_variable do not state a work type, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('J03', 'spans_stages', 'not_working', 'varies', 'varies', 'elevated',
     'Long-term unemployment with immediate support needs and a retirement goal raises difficulty.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; gate long_term_unemployed maps to not_working; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('J04', 'spans_stages', 'self_employed_or_commission', 'limited_or_no_cpf', 'varies', 'elevated',
     'Low self-employed income with a MediSave path and support needs raises planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate self_employed maps to self_employed_or_commission; sep_medisave maps to limited_or_no_cpf as a MediSave-only pattern, not an entitlement.'),
    ('J05', 'payout_age_65_plus', 'not_applicable', 'limited_or_no_cpf', 'varies', 'elevated',
     'Essential retirement income and assistance with very little CPF raise planning difficulty.',
     'Gate age_65plus maps to payout_age_65_plus; no work-type predicate, so work_income_type is not_applicable; cpf_low maps to limited_or_no_cpf as a pattern, not an entitlement.'),
    ('J06', 'payout_age_65_plus', 'not_applicable', 'varies', 'single', 'elevated',
     'A senior living alone without family support faces stability and access difficulty.',
     'Gate age_65plus maps to payout_age_65_plus; no work-type predicate, so work_income_type is not_applicable; living_alone and no_family_support map to single.'),
    ('J07', 'spans_stages', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'Debt distress, arrears and thin liquidity suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('J08', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'specialist_review_suggested',
     'Immediate survival after the loss of a main income earner, with dependants, suggests specialist review.',
     'No age-band predicate, so life_stage is spans_stages; remaining household work type is not stated, so work_income_type is not_applicable; children_dependent maps to dependants.'),
    ('K01', 'spans_stages', 'not_applicable', 'accumulating', 'varies', 'elevated',
     'CPF, housing and possible overseas assets for a long-term PR raise location difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; cpf_contrib indicates accumulating.'),
    ('K02', 'spans_stages', 'not_applicable', 'accumulating', 'varies', 'specialist_review_suggested',
     'foreign_pension and overseas_assets, with a transition in CPF and overseas assets, match the same multi-jurisdiction pattern as K06 and K08 and suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; cpf_contrib indicates accumulating even with foreign_pension present.'),
    ('K03', 'spans_stages', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'Cross-border cost, currency and residency when retiring in Malaysia suggest specialist review.',
     'retire_in_malaysia does not state an age band, so life_stage is spans_stages; no work-type or CPF-retirement predicate, so those fields are not_applicable and varies.'),
    ('K04', 'spans_stages', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'Foreign property, spending and currency exposure suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('K05', 'spans_stages', 'not_applicable', 'varies', 'couple', 'specialist_review_suggested',
     'Different retirement systems and eligibility for a mixed-nationality couple suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; foreign_pension plus pr_status is not a single CPF pattern, so cpf_retirement_situation is varies; mixed_nationality_couple and married map to couple.'),
    ('K06', 'spans_stages', 'salaried', 'limited_or_no_cpf', 'varies', 'specialist_review_suggested',
     'Non-CPF retirement planning for an Employment Pass holder suggests specialist review.',
     'No age-band predicate, so life_stage is spans_stages; gate employment_pass is treated as salaried because that pass is an employer-sponsored employment pass; no_cpf maps to limited_or_no_cpf as a pattern, not an entitlement.'),
    ('K07', 'spans_stages', 'salaried', 'limited_or_no_cpf', 'dependants', 'elevated',
     'Overseas family obligations and non-CPF savings raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; gate work_permit_or_spass is treated as salaried because those passes are employer-sponsored employment passes; no_cpf maps to limited_or_no_cpf as a pattern, not an entitlement; overseas_family_support maps to dependants.'),
    ('K08', 'spans_stages', 'not_applicable', 'limited_or_no_cpf', 'varies', 'specialist_review_suggested',
     'CPF gaps and overseas retirement assets after a return to Singapore suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; cpf_low maps to limited_or_no_cpf as a pattern, not an entitlement.'),
    ('L01', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'specialist_review_suggested',
     'Company-sale proceeds and retirement capital from a business exit suggest specialist review.',
     'retirement_soon is not a tight age band, so life_stage is spans_stages; sme_owner and business_equity map to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('L02', 'spans_stages', 'self_employed_or_commission', 'varies', 'varies', 'specialist_review_suggested',
     'Valuation uncertainty and exit risk for illiquid business shares suggest specialist review.',
     'No age-band predicate, so life_stage is spans_stages; business_equity and business_income map to self_employed_or_commission; no CPF-retirement predicate, so cpf_retirement_situation is varies.'),
    ('L03', 'spans_stages', 'not_working', 'payout_started', 'varies', 'elevated',
     'Integrating a private pension with CPF income raises planning difficulty.',
     'retired_status without an age-band predicate is not enough to choose a life-stage band, so life_stage is spans_stages; retired_status maps to not_working; cpf_income with retired_status maps to payout_started as a pattern, not an entitlement.'),
    ('L04', 'spans_stages', 'not_working', 'payout_started', 'varies', 'elevated',
     'Scheme-specific civil-service pension income integrated with CPF raises planning difficulty.',
     'retired_status without an age-band predicate is not enough to choose a life-stage band, so life_stage is spans_stages; retired_status maps to not_working; cpf_income with retired_status maps to payout_started as a pattern, not an entitlement.'),
    ('L05', 'spans_stages', 'not_applicable', 'varies', 'varies', 'elevated',
     'Vacancy, maintenance and net yields on a rental-income household raise planning difficulty.',
     'No age-band predicate, so life_stage is spans_stages; rental_income is asset income, not a work type, so work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('L06', 'spans_stages', 'not_applicable', 'varies', 'dependants', 'elevated',
     'International remittances and overseas dependants raise planning difficulty.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; overseas_family_support, family_transfers and high_dependency map to dependants.'),
    ('L07', 'spans_stages', 'not_applicable', 'varies', 'varies', 'specialist_review_suggested',
     'Estate liquidity, complex beneficiaries and charitable goals suggest specialist review.',
     'No age-band or work-type predicate, so life_stage is spans_stages and work_income_type is not_applicable; no CPF-retirement or household predicate, so those fields vary.'),
    ('L08', 'payout_age_65_plus', 'not_applicable', 'varies', 'single', 'specialist_review_suggested',
     'Safeguarding and protective referral for a senior exposed to exploitation suggest specialist review.',
     'Criteria age_65plus maps to payout_age_65_plus; no work-type predicate, so work_income_type is not_applicable; no CPF-retirement predicate, so cpf_retirement_situation is varies; living_alone maps to single.'),
]

HEADER = {
    "document_title": "Internal draft persona labels (SWEELAH-ISSUE-3, Refs #3)",
    "document_status": "INTERNAL_DRAFT",
    "visibility": "INTERNAL_ONLY_NOT_FOR_CONSUMER_UI_API_OR_EXPORTS",
    "owner": "Head of Product",
    "authored_by": "Engineering Lead, first pass derived from existing rules fields",
    "pending_review": "Pending Head of Product review of every record; Product owns the final values",
    "taxonomy_source": "Head of Product specification, Status: Proposed",
    "taxonomy_status": "Proposed",
    "label_status": DRAFT_STATUS,
    "evidence_level": EVIDENCE_NONE,
    "alignment": "Source of truth: retirepilot/retirepilot_rules_v1.2.json. Also PSD v2.7 section 3 and Appendix A, and docs/APPROVED_DECISIONS_v2.7.md decisions 1A, 2A, 3A and 7A.",
    "decision_1A": "No risk tier. Labels are not suitability advice or product recommendations.",
    "decision_2A": "cpf_retirement_situation values describe patterns only. No amounts and no entitlement claims.",
    "decision_3A": "Labels are internal only. They must not appear in the consumer UI, API or exports until reviewed. All personas are retained. Matching gates, weights and results are unchanged.",
    "decision_7A": "evidence_level is None: internal design, no research. Favourable consumer testing is not assumed.",
    "derivation_rule": "First pass derived from existing gate, criteria predicates, name, family and planning_focus. Use varies or spans_stages rather than guessing an age band, work type, CPF situation or household context.",
    "usage_restriction": "Do not use these labels to infer a user's age, CPF status or any other attribute. Do not change matching gates, weights or results. Do not use them to sort, filter or prioritise personas before the decision 7A research gate.",
    "hop_review": "Head of Product review, Status: Proposed: four hundred and seventy-five of four hundred and eighty values accepted; five field corrections applied. Labels stay DRAFT_NOT_INDEPENDENTLY_REVIEWED with evidence_level None.",
    "planning_complexity_reason_visibility": "INTERNAL_ONLY (decision 3A). planning_complexity_reason text, including specialist review and protective referral, must not appear in the consumer UI, API, exports or the assistant.",
    "phase_nine": "NO-GO",
}


def _rationale(rec: dict, note: str) -> str:
    predicates = ", ".join(item["predicate"] for item in rec["criteria"])
    return (
        f"Gate {rec['gate']}; criteria {predicates}; "
        f"planning_focus {rec['planning_focus']}. {note}"
    )


def build(rules: dict | None = None) -> dict:
    rules = rules or json.loads(RULES_PATH.read_text(encoding="utf-8"))
    personas = rules["personas"]
    by_id = {row[0]: row for row in ROWS}
    if set(by_id) != set(personas):
        raise SystemExit("ROWS must cover exactly the rules-file persona ids")
    records = []
    for pid, rec in personas.items():
        row = by_id[pid]
        records.append({
            "persona_id": pid,
            "family": rec["family"],
            "name": rec["name"],
            "life_stage": row[1],
            "work_income_type": row[2],
            "cpf_retirement_situation": row[3],
            "household_context": row[4],
            "planning_complexity": row[5],
            "planning_complexity_reason": row[6],
            "label_status": DRAFT_STATUS,
            "evidence_level": EVIDENCE_NONE,
            "rationale": _rationale(rec, row[7]),
        })
    doc = dict(HEADER)
    doc["records"] = records
    return doc


def dumps(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[0]) if argv else DEFAULT_OUT
    out.write_text(dumps(build()), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
