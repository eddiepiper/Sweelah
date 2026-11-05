# SweeLah financial product intelligence library (v1 discovery)

**Snapshot:** 2026-11-05 (Singapore)  
**Status:** RESEARCH / SYNTHETIC ONLY. **Phase 9: NO-GO.**  
**Institution coverage:** OCBC Singapore retail banking and Great Eastern Singapore insurance, not exhaustive.

## What is implemented

- \`product_library/products_v1.json\`: **99** identifiable, versioned discovery entries (OCBC 49; Great Eastern 50) across nine product families. Each record contains stable product ID, institution, market, family, listing evidence, links to existing financial-engine contracts F01-F18, and separate *unverified* eligibility / financial-terms states.
- \`product_library/sources_v1.json\`: official public OCBC/Great Eastern URL references with the 2026-11-05 review date and a scoped statement of what each source supports.
- \`product_library/rules_v1.json\`: **four non-executable candidate/source-checked rule sets** demonstrating how published criteria can be recorded with evidence, scope, observation/effective date and explicit limitations. Nothing is marked approved.
- \`retirepilot/product_library.py\`: versioned JSON loader, validation (source domains, references, duplicate IDs, rule conditions), fail-closed threshold evaluator, and limited customer-owned holdings input adapter.
- \`tests/test_product_library.py\`: synthetic checks for loading, source integrity, unapproved rules, unknowns, ambiguity, invalid amounts and contract data integrity.

This is an **additive module**. The existing \`retirepilot/core.py\`, CPF, income and scenario engines, 18 financial contracts and 96 provisional archetypes remain unchanged.

## Architecture and data-flow contract

1. **Public product directory:** identify a product and its categories. This does **not** establish full eligibility, active new-business availability, a guaranteed rate, benefits, underwriting acceptance, or a bank/insurer approval.
2. **Product-specific rule authoring:** extract each age, residency, income, relationship, funding and coverage condition from the *individual* policy brochure/application terms, including exceptions, version and signed-off effective date. Store each rule with evidence and reviewer.
3. **Human review / approval:** current statuses are \`candidate\`, \`source_checked\`, \`approved\`, \`retired\`. The published seed has no \`approved\` rules. Do not change statuses merely because AI extracted them.
4. **Bounded deterministic evaluation:** \`evaluate_product(product_id, facts, as_of)\` produces \`requires_review\`, \`published_conditions_met\`, or \`published_conditions_not_met\`. Even the latter two **never** imply full product eligibility, credit approval, insurance acceptance or suitability.
5. **Customer-owned contract records:** after a separate identity/authority and source-document verification step, \`holding_engine_inputs\` exposes a *small explicit subset* of reported balances, loan payments and premiums. It excludes unverified payouts, hypothetical claims and marketing rates.
6. **Core financial engines:** existing F01-F18 contracts and household projection code remain the intended targets; this release does **not** wire product outputs into projections. Avoid double counting or treating contingent insurance payouts as guaranteed income.

## Registry contract

\`\`\`text
products_v1.json
  version, catalogue_as_of, products[]
    id, name, provider, market, family, listing_context
    new_business_status, eligibility_verification
    financial_terms_verification, source_ids[], engine_contracts[]

sources_v1.json
  version, sources[]
    id, url, checked_on, evidence_scope

rules_v1.json
  version, rule_sets[]
    id, product_id, status, coverage, effective_from, effective_to
    source_ids[], conditions[], limitations, approval?
\`\`\`

All published product records have \`eligibility_verification=unverified\` and \`financial_terms_verification=unverified\`. Directory appearance is not evidence of 2026 issue availability. An \`official_directory_or_homepage\` context means the name was observed on a public site, not that the policy is currently issued; \`servicing_only\` means there is no verified new-application availability; \`research_discovery_not_individually_checked\` requires direct product-level confirmation.

**Effective-date caveat:** the seed rule sets use 2026-11-05 as the *observation baseline*, not a verified legal/product-terms effective date. They must not be approved or executed until the true terms effective date has been confirmed in the specific source document and its exceptions and eligibility scope reviewed. The current \`approved\` path in Python is an internal technical mechanism, not an operational approval workflow.

## Python usage (synthetic facts only)

\`\`\`python
from retirepilot.product_library import load_registry, evaluate_product, holding_engine_inputs

registry = load_registry()
print(len(registry["catalogue"]["products"]))  # 99
print(evaluate_product("ocbc.account.360-account",
                       {"age_years": 45}, "2026-11-05", registry))
# => requires_review: pending_independent_rule_approval

print(holding_engine_inputs("ocbc.account.360-account",
    {"as_of": "2026-11-05",
     "owner_authority_verified": False,
     "contract_terms_verified": False,
     "cash_balance_sgd": "10000"}, registry))
# => requires_review: owned_contract_and_authority_evidence_required
\`\`\`

Run: \`python -m pytest -q tests/test_product_library.py\`. The existing root CI runs this as part of \`pytest -q\`.

## Next evidence and engine work

1. Obtain **product-specific brochures, insurance policy wordings, loan terms, pricing fee tables, application T&Cs, addendum/rider definitions and source hashes**, then approve field-level rules with effective dates. Catalogues alone do not satisfy this gate.
2. Replace the discovery-only list with individual variant/rider records and coverage-completeness tracking. Include historical/servicing-only terms for existing policyholders.
3. Model conditional financial terms and payouts separately: guaranteed vs non-guaranteed, coverage/claim triggers, repayment schedules, temporary promotional tiers and exclusions. No payout enters forecast without verified contract evidence and entitlement.
4. Implement independent policy approval and expiry controls, change-detection reviews, full source audit trail, and regression fixtures covering age boundaries, income tiers, product variants, residency and adverse outcomes.
5. Integrate approved product-term snapshots into F01-F18, with reproducible numerical examples, verified account/insurance holdings, explicit consent and no double-counting.
6. Independently reconcile CPF lifetime modelling, medical/insurance assumptions and retirement scenarios. Existing release gates G2-G8 still apply.

**Security:** no customer identity, medical disclosures, statements, real policy documents, account numbers or balances belong in this public-reference GitHub source tree. Any future holdings provider requires real authenticated, consent-scoped access controls. Local boolean evidence flags in the demo do **not** prove a real person's identity or entitlement.

## Official source entry points (reviewed 2026-11-05)

- OCBC deposits: https://www.ocbc.com/personal-banking/deposits
- OCBC 360: https://www.ocbc.com/personal-banking/deposits/360-savings-account
- OCBC loans: https://www.ocbc.com/personal-banking/loans
- OCBC credit cards: https://www.ocbc.com/personal-banking/cards/credit-card
- OCBC card servicing: https://www.ocbc.com/personal-banking/help-and-support/cards/general
- Great Eastern insurance catalogue: https://www.greateasternlife.com/sg/en/personal-insurance/our-products.html
- Great Eastern wealth/retirement: https://www.greateasternlife.com/sg/en/personal-insurance/our-products/segments/wealth-retirement.html

Do not infer facts not stated in these pages; always prefer the specific current policy or product document and verify changes independently.
