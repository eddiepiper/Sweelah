"""Independent 2026/27 CPF age-boundary expectations for existing bounded references.

Sources: CPF employee and platform contribution tables, and 2026 SEP MediSave
rate table. These cases do not validate a complete financial engine.
"""

import pytest

from retirepilot.cpf_retirement_v26 import CPFUnsupportedCase, transition_at_55
from retirepilot.statutory_2026 import (
    employee_ow_cpf,
    platform_cpf,
    self_employed_medisave_2026,
)


@pytest.mark.parametrize(
    "year,age,prior_rates,following_rates",
    [
        (2026, 55, ("17", "20"), ("16", "18")),
        (2026, 60, ("16", "18"), ("12.5", "12.5")),
        (2026, 65, ("12.5", "12.5"), ("9", "7.5")),
        (2026, 70, ("9", "7.5"), ("7.5", "5")),
        (2027, 55, ("17", "20"), ("16.5", "19")),
        (2027, 60, ("16.5", "19"), ("13", "13")),
        (2027, 65, ("13", "13"), ("9", "7.5")),
        (2027, 70, ("9", "7.5"), ("7.5", "5")),
    ],
)
def test_employee_age_rate_changes_month_after_birthday(year, age, prior_rates, following_rates):
    dob = f"{year - age}-05-20"

    def rates(month):
        result = employee_ow_cpf(
            dob=dob, residency="SG", month=f"{year}-{month:02d}", monthly_ordinary_wages="8000"
        )
        assert result["status"] == "bounded_reference"
        return result["employer_rate_pct"], result["worker_rate_pct"]

    assert rates(4) == prior_rates
    assert rates(5) == prior_rates
    assert rates(6) == following_rates


@pytest.mark.parametrize(
    "age,opted_in,prior_rate,following_rate",
    [
        (35, True, "13", "14"),
        (45, True, "14", "15"),
        (50, True, "15", "15.5"),
        (60, True, "15.5", "12.5"),
        (65, True, "12.5", "9.5"),
        (70, True, "9.5", "5.5"),
        (35, False, "8", "9"),
        (45, False, "9", "10"),
        (50, False, "10", "10.5"),
    ],
)
def test_platform_age_rate_changes_month_after_birthday(age, opted_in, prior_rate, following_rate):
    dob = f"{2026 - age}-05-20"

    def rate(month):
        result = platform_cpf(
            dob=dob,
            month=f"2026-{month:02d}",
            monthly_gross="3000",
            transport="car",
            opted_in=opted_in,
        )
        assert result["status"] == "bounded_reference"
        return result["worker_rate_pct"]

    assert rate(4) == prior_rate
    assert rate(5) == prior_rate
    assert rate(6) == following_rate


def test_employee_2027_rule_change_applies_on_first_january():
    inputs = dict(dob="1967-05-20", residency="SG", monthly_ordinary_wages="8000")
    prior = employee_ow_cpf(month="2026-12", **inputs)
    following = employee_ow_cpf(month="2027-01", **inputs)
    assert (prior["employer_rate_pct"], prior["worker_rate_pct"]) == ("16", "18")
    assert (following["employer_rate_pct"], following["worker_rate_pct"]) == ("16.5", "19")


def test_platform_1995_birth_cohort_requires_opt_in_confirmation_for_older_worker():
    inputs = dict(month="2026-05", monthly_gross="3000", transport="car", opted_in=None)
    older = platform_cpf(dob="1994-12-31", **inputs)
    mandatory = platform_cpf(dob="1995-01-01", **inputs)
    assert older["status"] == "requires_review"
    assert mandatory["status"] == "bounded_reference"
    assert mandatory["increased_contribution_pathway"] is True


def test_sep_2026_age_band_uses_age_on_first_january():
    def medisave(dob):
        result = self_employed_medisave_2026(
            dob=dob,
            annual_nti="12000",
            non_pensioner=True,
            platform_earnings_excluded=True,
        )
        assert result["status"] == "bounded_reference"
        return result["age_at_jan1"], result["annual_medisave_reference_sgd"]

    assert medisave("1976-01-02") == (49, "600.00")
    assert medisave("1976-01-01") == (50, "630.00")


def test_age_55_account_snapshot_only_runs_on_exact_birthday():
    common = dict(dob="1971-05-20", oa="100000", sa="160000", ma="50000", cpf_membership_confirmed=True)
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(as_of="2026-05-19", **common)
    on_day = transition_at_55(as_of="2026-05-20", **common)
    assert on_day["event_date"] == "2026-05-20"
    assert on_day["closing"]["RA"] == "220400"
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(as_of="2026-05-21", **common)
