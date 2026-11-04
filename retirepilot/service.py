"""Composed API-independent phase 4-6 assessment."""
from .core import validate,monthly_snapshot,compare,project
from .projection_v22 import incomplete_financial_records
from .adapter import classify_household
from .policy import policy_reference
from .assistant import plan_actions,answer
from .statutory_2026 import review_household_contributions

def public_persona_summary(raw):
    """Consumer view only: preserve internal ranking, never expose numerical scores.

    The raw rule evaluation remains available to local test functions, but is not
    returned by the customer-facing API. Matching is descriptive, provisional,
    and not a probability, eligibility result or retirement suitability rating.
    """
    top=[{'id':p['id'], 'name':p['name'], 'status':'provisional_pattern',
          'explanation':'A possible planning situation inferred from reported facts; correct facts to refine it.'}
         for p in raw['user_visible_top_three']]
    return {'evaluated':raw['evaluated'], 'rule_version':raw['rule_version'],
            'user_visible_top_three':top,
            'display_policy':'descriptions_only_unvalidated',
            'warnings':['These are provisional descriptions, not likelihoods, suitability scores, benefit eligibility or priority rankings.']}


def evaluate(profile,scenarios=None,projection_years=15):
    warnings=validate(profile)
    snap=monthly_snapshot(profile)
    cl=classify_household(profile)
    pol=policy_reference(profile)
    missing=[name for name in ('income_streams','liabilities','expenses','assets') if name not in profile]
    missing += incomplete_financial_records(profile)
    if snap['expenses_monthly'] is None or snap['liquid_assets'] is None or snap['net_cash_income_monthly'] is None or missing:
        required=missing + (['expenses'] if snap['expenses_monthly'] is None and 'expenses' not in missing else []) + (['accessible liquid assets'] if snap['liquid_assets'] is None and 'assets' not in missing else [])
        proj={'status':'blocked_missing_required_data','required':required,'baseline':None,'comparison':None}
    else:
        base=project(profile,years=projection_years)
        proj={'status':'conditional_estimate','baseline':base,'comparison':compare(profile,scenarios,years=projection_years) if scenarios else None}
    actions=plan_actions(profile,cl,snap)
    return {'version':'2.7.0-decisions-approved','status':'research_prototype_only','profile_id':profile.get('id'),'cash_flow':snap,
            'classification':public_persona_summary(cl),'singapore_policy_references':pol,'cpf_contribution_review':review_household_contributions(profile),'projection':proj,'recommended_review_actions':actions,
            'warnings':warnings,'limitations':['No live CPF, MAS, bank, IRAS, or government connections','Persona patterns are provisional; numeric weights and confidence scores are not consumer-visible',
             'Financial projection is scenario math, not a guaranteed return or licensed advice', 'No real customer financial data, authenticated multi-adult consent, or household sharing permitted; local demo is unauthenticated']}
