"""CPF retirement *reference* calculations, not a complete CPF simulator.

Deterministic cohort-specific transfer on the 55th birthday only, plus
published CPF LIFE Standard Plan illustrations with exact table lookups.
Do NOT forecast future CPF interest, payroll allocations, top-ups, LIFE
premiums, official eligibility, property pledges or payouts from balances.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
from . import core as _core

SOURCE_RA='https://www.cpf.gov.sg/service/article/what-happens-to-my-cpf-savings-when-i-turn-55'
SOURCE_SA='https://www.cpf.gov.sg/service/article/what-is-the-closure-of-special-account-for-members-aged-55-and-above-about'
SOURCE_FRS='https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum'
SOURCE_LIFE='https://www.cpf.gov.sg/service/article/how-much-cpf-payouts-can-i-get-every-month'
FRS_55={2026: Decimal('220400'),2027: Decimal('228200')}
# Exact 2026 male Standard Plan reference rows (savings in RA at 55,
# official illustration of CPF LIFE payout starting at 65 or 70).
LIFE_2026_STANDARD_MALE={
    Decimal('50000'):(Decimal('490'),Decimal('670')),
    Decimal('110200'):(Decimal('950'),Decimal('1280')),
    Decimal('150000'):(Decimal('1250'),Decimal('1670')),
    Decimal('220400'):(Decimal('1780'),Decimal('2380')),
    Decimal('300000'):(Decimal('2380'),Decimal('3170')),
    Decimal('440800'):(Decimal('3440'),Decimal('4580')),
}

class CPFUnsupportedCase(ValueError): pass

def _nonnegative_decimal(value, field):
    if isinstance(value, bool): raise CPFUnsupportedCase(field+' must be numeric')
    try: n=Decimal(str(value))
    except (InvalidOperation,TypeError,ValueError): raise CPFUnsupportedCase(field+' must be numeric')
    if not n.is_finite() or n<0:raise CPFUnsupportedCase(field+' must be nonnegative and finite')
    return n

def _attained_age_date(born: date, age: int) -> date:
    """First date on which a person born on ``born`` attains ``age``.

    Thin wrapper over core.attained_age_date (INTERNAL ASSUMPTION: 29 Feb ->
    1 Mar in a common year). Out-of-range years raise CPFUnsupportedCase.
    """
    return _core.attained_age_date(born, age, error=CPFUnsupportedCase)

def transition_at_55(*, dob:str, as_of:str, oa, sa, ma, existing_ra='0', cpf_membership_confirmed:bool=False, property_pledge:bool=False):
    """Transfers SA first, OA second into a new RA up to cohort FRS.

    This isolated snapshot is valid only on the date the member attains 55 for
    cohorts 2026/27; no accrued interest or past/future events are simulated.
    """
    try: birthday=date.fromisoformat(dob); today=date.fromisoformat(as_of)
    except (ValueError,TypeError): raise CPFUnsupportedCase('Valid ISO date of birth and as_of required')
    if today != _attained_age_date(birthday, 55):
        raise CPFUnsupportedCase('Only an exact 55th-birthday snapshot is supported; cannot reconstruct historical balances')
    if today.year not in FRS_55:
        raise CPFUnsupportedCase('Only 2026 and 2027 55-year-old cohorts have verified FRS in this module')
    if cpf_membership_confirmed is not True:raise CPFUnsupportedCase('Verified CPF membership required')
    if property_pledge:raise CPFUnsupportedCase('Property pledge/withdrawal scenarios require official case-specific review')
    oa0=_nonnegative_decimal(oa,'oa');sa0=_nonnegative_decimal(sa,'sa');ma0=_nonnegative_decimal(ma,'ma')
    ra0=_nonnegative_decimal(existing_ra,'existing_ra')
    if ra0!=0:raise CPFUnsupportedCase('Existing RA nonzero; cannot model creation from initial zero RA')
    frs=FRS_55[today.year]
    sa_to_ra=min(sa0,frs)
    oa_to_ra=min(oa0,frs-sa_to_ra)
    sa_remainder=sa0-sa_to_ra
    ra_new=sa_to_ra+oa_to_ra
    oa_new=oa0-oa_to_ra+sa_remainder
    result={'status':'bounded_reference','event_date':today.isoformat(),'frs_cohort_year':today.year,
      'frs':str(frs),'opening':{'OA':str(oa0),'SA':str(sa0),'MA':str(ma0),'RA':str(ra0)},
      'transfers':{'SA_to_RA':str(sa_to_ra),'OA_to_RA':str(oa_to_ra),'SA_to_OA_excess':str(sa_remainder)},
      'closing':{'OA':str(oa_new),'SA':'0','MA':str(ma0),'RA':str(ra_new)},
      'below_FRS':ra_new<frs,'sources':[SOURCE_RA,SOURCE_SA,SOURCE_FRS],
      'limitations':['No interest credit or contribution timing','No property pledge, withdrawal, top-up or government grant','No CPF LIFE premium/payout calculation','2026/27 cohort and precise birthday snapshot only']}
    assert oa0+sa0+ma0==oa_new+ma0+ra_new
    return result

def cpf_life_official_table_2026(*, ra_age55, payout_start_age:int, plan:str='Standard', reference_member:str='male'):
    """Exact published 2026 illustrative table row; not a personalised payout estimate."""
    if plan!='Standard' or reference_member!='male' or payout_start_age not in (65,70):
        raise CPFUnsupportedCase('Published lookup only for male Standard Plan examples starting at 65 or 70')
    amount=_nonnegative_decimal(ra_age55,'ra_age55')
    if amount not in LIFE_2026_STANDARD_MALE:
        raise CPFUnsupportedCase('Amount is not an exact published table row; interpolation and personalised estimates prohibited')
    pos=0 if payout_start_age==65 else 1
    return {'status':'published_illustration_not_personal_estimate','cohort_year':2026,
      'starting_RA_at_55':str(amount),'payout_start_age':payout_start_age,
      'illustrative_monthly_SGD':str(LIFE_2026_STANDARD_MALE[amount][pos]),
      'plan':plan,'reference_member':reference_member,'source':SOURCE_LIFE,
      'limitations':['Published example, not a quote for a real member','No private CPF inputs, accrued interest or annuity pricing reproduced','Use CPF Retirement Payout Planner for official personal estimate']}
