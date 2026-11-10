"""SWEELAH-ISSUE-9 / Refs #9: partial-month boundary golden cases (synthetic only).

Expected values come from an independent calendar-day oracle written here, not from
the engine: each day in [start, end) contributes amount / days-in-that-month.
Age boundaries follow the engine's own ``core.age_on`` definition: a person
attains age N on the first date where ``age_on(dob, date) == N``. For a 29 Feb
birthday in a common year, that is 1 March.
"""
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import pytest

from retirepilot.core import age_on, project

CENT = Decimal("0.01")
ZERO_RATES = {"inflation_pct": "0", "nominal_return_pct": "0", "cash_yield_pct": "0", "income_growth_pct": "0"}


def attains(dob, age):
    """Independent oracle: first calendar date on which age_on reports ``age``."""
    born = date.fromisoformat(dob)
    d = date(born.year + age, born.month, 1)
    while age_on(dob, d) < age:
        d += timedelta(days=1)
    return d


def day_prorated(amount, start, end):
    """Calendar-day reference: per-year totals of amount/days_in_month over [start, end)."""
    totals, d = {}, start
    while d < end:
        totals[d.year] = totals.get(d.year, Decimal(0)) + Decimal(amount) / Decimal(monthrange(d.year, d.month)[1])
        d += timedelta(days=1)
    return {y: str(v.quantize(CENT, ROUND_HALF_UP)) for y, v in totals.items()}


def profile(dob, as_of, end_age, **goal):
    return {
        "id": "RP-SYNTH-ISSUE9", "as_of": as_of, "currency": "SGD", "primary_id": "P1",
        "persons": [{"id": "P1", "role": "primary", "dob": dob, "residency": "SG", "marital_status": "single"}],
        "relationships": [], "income_streams": [], "expenses": [], "liabilities": [], "assets": [],
        "goal": {"projection_end_age": end_age, **goal}, "assumptions": dict(ZERO_RATES),
    }


def stream(kind="rental", amount="7200", **extra):
    return {"id": "I-TEST", "owner_id": "P1", "type": kind, "gross_monthly": amount, "worker_cpf_monthly": "0",
            "tax_reserve_monthly": "0", "cash_deductions_monthly": "0", "operating_costs_monthly": "0", **extra}


def by_year(result, key):
    return {row["year"]: row[key] for row in result["rows"]}


# --- Anniversary on the 1st, mid-month, last day, and partial start month -----------------

@pytest.mark.parametrize("dob", ["1974-05-01", "1974-05-20", "1974-05-31", "1974-01-31", "1974-12-31", "1974-02-28"])
@pytest.mark.parametrize("as_of", ["2026-11-03", "2027-01-01", "2026-12-31"])
def test_terminal_month_income_and_expense_match_calendar_days(dob, as_of):
    x = profile(dob, as_of, 53)
    x["income_streams"] = [stream()]
    x["expenses"] = [{"id": "E-TEST", "category": "other", "amount_monthly": "3100"}]
    result = project(x)
    horizon = attains(dob, 53)
    assert by_year(result, "income") == day_prorated("7200", date.fromisoformat(as_of), horizon)
    assert by_year(result, "spending") == day_prorated("3100", date.fromisoformat(as_of), horizon)


def test_issue_reference_case_still_33212_90():
    x = profile("1974-05-20", "2027-01-01", 53)
    x["income_streams"] = [stream()]
    assert by_year(project(x), "income") == {2027: "33212.90"}


# --- Leap-year (29 Feb) boundaries: must agree with age_on --------------------------------

def test_leap_day_birthday_horizon_includes_28_february_of_common_year():
    # Born 29 Feb 1976: age_on says still 52 on 28 Feb 2029 and 53 on 1 Mar 2029.
    x = profile("1976-02-29", "2029-01-01", 53)
    x["income_streams"] = [stream()]
    assert by_year(project(x), "income") == {2029: "14400.00"}  # Jan + all of Feb


def test_leap_day_birthday_starts_age_income_not_paid_a_day_early():
    # Payout from age 53 must start 1 Mar 2029, not 28 Feb 2029 (overstatement).
    x = profile("1976-02-29", "2029-01-01", 54)
    x["income_streams"] = [stream(starts_age=53)]
    assert by_year(project(x), "income") == {2029: "72000.00", 2030: "14400.00"}


def test_leap_day_birthday_retirement_cutoff_keeps_last_working_day():
    x = profile("1976-02-29", "2029-01-01", 54, retirement_age=53)
    x["income_streams"] = [stream(kind="salary")]
    assert by_year(project(x), "income") == {2029: "14400.00", 2030: "0.00"}


def test_leap_day_birthday_age_limited_expense_not_dropped_early():
    # Expense until P1 is 53 must cover all of Feb 2029; dropping 28 Feb understates
    # spending and so overstates net cash flow.
    x = profile("1976-02-29", "2029-01-01", 54)
    x["expenses"] = [{"id": "E-TEST", "category": "other", "amount_monthly": "2800",
                      "person_id": "P1", "end_person_age": 53}]
    assert by_year(project(x), "spending") == {2029: "5600.00", 2030: "0.00"}


def test_leap_day_birthday_in_leap_year_unchanged():
    # Born 29 Feb 1976, turns 52 on 29 Feb 2028 (leap year): Jan + 28/29 of Feb.
    x = profile("1976-02-29", "2028-01-01", 52)
    x["income_streams"] = [stream(amount="2900")]
    assert by_year(project(x), "income") == {2028: "5700.00"}


@pytest.mark.parametrize("dob", ["1976-02-29", "1972-02-29", "1974-05-20", "1974-05-31", "1975-03-01"])
@pytest.mark.parametrize("as_of", ["2026-02-15", "2026-11-03", "2028-02-29"])
def test_starts_and_ends_age_flows_match_calendar_days(dob, as_of):
    a = date.fromisoformat(as_of)
    age = age_on(dob, a)
    x = profile(dob, as_of, age + 2)
    x["income_streams"] = [stream(starts_age=age + 1)]
    x["expenses"] = [{"id": "E-TEST", "category": "other", "amount_monthly": "3100",
                      "person_id": "P1", "end_person_age": age + 1}]
    result = project(x)
    switch, horizon = attains(dob, age + 1), attains(dob, age + 2)
    exp_income = day_prorated("7200", switch, horizon)
    exp_spend = day_prorated("3100", a, switch)
    years = {row["year"] for row in result["rows"]}
    assert by_year(result, "income") == {y: exp_income.get(y, "0.00") for y in years}
    assert by_year(result, "spending") == {y: exp_spend.get(y, "0.00") for y in years}


# --- Terminal month: debt cash/CPF, interest and returns use full-month denominator ------

def test_terminal_month_debt_and_returns_use_full_calendar_month():
    x = profile("1974-05-20", "2027-05-01", 53)
    x["persons"][0]["cpf_balances"] = {"OA": "50000"}
    x["assumptions"].update({"nominal_return_pct": "6", "cash_yield_pct": "2"})
    x["assets"] = [{"id": "A-C", "type": "cash", "value": "31000", "accessible": True, "owners": {"P1": "1"}},
                   {"id": "A-I", "type": "investment", "value": "62000", "accessible": True, "owners": {"P1": "1"}}]
    x["liabilities"] = [{"id": "L-T", "type": "mortgage", "balance": "120000", "annual_interest_pct": "3.1",
                         "cash_payment_monthly": "1550", "cpf_payment_monthly": "620",
                         "cpf_payment_by_owner_monthly": {"P1": "620"}, "remaining_years": 10,
                         "owners": {"P1": "1"}}]
    row = project(x)["rows"][0]
    f = Decimal(19) / Decimal(31)  # 1-19 May of a 31-day month
    q = lambda v: str(v.quantize(CENT, ROUND_HALF_UP))
    assert row["months_modelled"] == 1
    assert row["debt_cash_payments"] == q(Decimal("1550") * f)
    assert row["debt_cpf_payments"] == q(Decimal("620") * f)
    assert row["debt_interest"] == q(Decimal("120000") * Decimal("0.031") / 12 * f)
    m_inv = (Decimal("1.06") ** (Decimal(1) / Decimal(12))) - 1
    m_cash = (Decimal("1.02") ** (Decimal(1) / Decimal(12))) - 1
    assert row["portfolio_gain"] == q(Decimal("62000") * m_inv * f)
    assert row["cash_interest"] == q(Decimal("31000") * m_cash * f)
