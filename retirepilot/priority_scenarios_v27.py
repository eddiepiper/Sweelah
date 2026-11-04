"""Five approved priority scenario *previews*, not end-to-end life event engines.

Only show bounded arithmetic from explicitly supplied figures. Never infer a legal
entitlement, CPF LIFE payout, housing eligibility, insurance payout or tax result.
For complex scenarios, a preview must not modify the core household forecast.
"""
from decimal import Decimal
from .core import ValidationError, dec, money

PRIORITY_IDS=('S020','S030','S004','S016','S012')
PRIORITY_STATUS={
 'S020':('housing_downsizing','LIMITED_PROCEEDS_PREVIEW_ONLY'),
 'S030':('cpf_life_start_timing','MEMBER_ESTIMATES_COMPARISON_ONLY'),
 'S004':('part_time_retirement','LIMITED_EARNED_CASH_PREVIEW_ONLY'),
 'S016':('parent_care','LIMITED_RECURRING_COST_PREVIEW_ONLY'),
 'S012':('family_transition_divorce','BLOCKED_PENDING_LEGAL_AND_HOUSEHOLD_CONSENT'),
}

def _amount(params,name,*,positive=False):
    if name not in params:raise ValidationError(f'{name}: explicit member-provided value required')
    value=dec(params[name],name)
    if value<0 or (positive and value==0):raise ValidationError(f'{name}: nonnegative amount required')
    return value

def preview_priority_scenario(sid, params):
    """Return a limited planning sensitivity; no authoritative personal advice."""
    if sid not in PRIORITY_IDS:raise ValidationError('Not one of the five approved priority scenarios')
    if not isinstance(params,dict):raise ValidationError('scenario inputs must be an object')
    family,status=PRIORITY_STATUS[sid]
    output={'scenario_id':sid,'family':family,'status':status,'implemented_as':'bounded_preview_not_full_event',
            'personalised_entitlement_or_advice':False,'may_post_to_household_projection':False}
    if sid=='S020':
        if params.get('cpf_refund_source')!='member_transcribed_official_cpf_property_refund':
            raise ValidationError('housing downsizing requires official member-supplied CPF property refund amount')
        sale=_amount(params,'sale_price',positive=True)
        selling=_amount(params,'sale_costs')
        loan=_amount(params,'outstanding_mortgage')
        refund=_amount(params,'cpf_refund_official')
        replacement=_amount(params,'replacement_home_total_cost')
        available=sale-selling-loan-refund
        if available<0:raise ValidationError('negative sale proceeds require a financing shortfall model')
        net=available-replacement
        output.update({'sale_cash_proceeds_after_cpf_refund':money(available),
                       'cash_after_replacement_purchase':money(net),
                       'meaning':'Cash arithmetic only; no CPF account crediting, stamp duty, HDB eligibility or timeline assumed'})
    elif sid=='S030':
        if params.get('estimate_source')!='member_transcribed_official_cpf_estimate':
            raise ValidationError('payout timing must compare two member-transcribed official CPF LIFE estimates')
        p65=_amount(params,'official_monthly_at_65',positive=True)
        p70=_amount(params,'official_monthly_at_70',positive=True)
        output.update({'monthly_at_65':money(p65),'monthly_at_70':money(p70),
                       'monthly_cash_difference_70_less_65':money(p70-p65),
                       'meaning':'User-supplied payout quotations compared; no lifetime break-even or actuarial calculation'})
    elif sid=='S004':
        current=_amount(params,'current_net_earned_cash_monthly')
        part=_amount(params,'part_time_net_earned_cash_monthly')
        if part>current:raise ValidationError('part-time cash preview requires net part-time income no higher than baseline')
        months=params.get('months')
        if isinstance(months,bool) or not isinstance(months,int) or months<1 or months>120:
            raise ValidationError('months must be an integer 1-120')
        output.update({'net_cash_change_monthly':money(part-current),
                       'period_cash_change':money((part-current)*months),
                       'meaning':'Comparison of explicitly net-of-deductions income only; CPF/tax future recalculation omitted'})
    elif sid=='S016':
        care=_amount(params,'additional_care_cost_monthly',positive=True)
        months=params.get('months')
        if isinstance(months,bool) or not isinstance(months,int) or months<1 or months>120:
            raise ValidationError('months must be an integer 1-120')
        output.update({'extra_monthly_cost':money(care),'period_cash_cost':money(care*months),
                       'meaning':'Illustrative recurring care costs only; leave, insurance and subsidies omitted'})
    elif sid=='S012':
        output.update({'meaning':'Legal separation, custody, property and maintenance must not be generated without independently documented legal and household-consent inputs',
                       'required_to_unblock':['independent legal assessment','authenticated consent for each adult','verified division and obligations','domain-specific financial engine']})
    return output
