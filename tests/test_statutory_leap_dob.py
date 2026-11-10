"""Leap-day dates of birth must not crash statutory CPF band lookup.

Synthetic dates only. The 1 March common-year convention below is an
INTERNAL ASSUMPTION aligned with core.age_on; it is not checked against
the CPF Board or any statutory convention (Phase 7 external review skipped).
"""

from datetime import date, timedelta

import pytest

from retirepilot.core import age_on
from retirepilot.statutory_2026 import (
    _band_index,
    employee_ow_cpf,
    platform_cpf,
    self_employed_medisave_2026,
)

# Valid 29-Feb dates of birth (those years are leap years).
DOB_TURNS_55_IN_2027 = "1972-02-29"  # 55th attained-age date: 2027-03-01 (common)
DOB_TURNS_50_IN_2026 = "1976-02-29"  # 50th attained-age date: 2026-03-01 (common)
DOB_TURNS_60_IN_2028 = "1968-02-29"  # 60th attained-age date: 2028-02-29 (leap)
EMPLOYEE_CUTOFFS = [55, 60, 65, 70]
PLATFORM_CUTOFFS = [35, 45, 50, 55, 60, 65, 70]


def _employee(dob, month):
    return employee_ow_cpf(
        dob=dob, residency="SG", month=month, monthly_ordinary_wages="8000"
    )


def _platform(dob, month, opted_in=True):
    return platform_cpf(
        dob=dob,
        month=month,
        monthly_gross="3000",
        transport="car",
        opted_in=opted_in,
    )


def test_age_on_29_feb_attains_new_age_on_1_mar_in_common_year():
    dob = DOB_TURNS_55_IN_2027
    assert date.fromisoformat("2027-03-01").year % 4 != 0  # 2027 is a common year
    assert age_on(dob, date(2027, 2, 28)) == 54
    assert age_on(dob, date(2027, 3, 1)) == 55


def test_age_on_29_feb_attains_new_age_on_29_feb_in_leap_year():
    dob = DOB_TURNS_60_IN_2028
    assert date(2028, 2, 29)  # 2028 is a leap year
    assert age_on(dob, date(2028, 2, 28)) == 59
    assert age_on(dob, date(2028, 2, 29)) == 60
    assert age_on(dob, date(2028, 3, 1)) == 60


@pytest.mark.parametrize(
    "dob,month",
    [
        (DOB_TURNS_55_IN_2027, "2026-11"),  # 55th anniversary year (2027) is common
        (DOB_TURNS_55_IN_2027, "2027-02"),
        (DOB_TURNS_55_IN_2027, "2027-03"),
        (DOB_TURNS_55_IN_2027, "2027-04"),
        (DOB_TURNS_50_IN_2026, "2026-03"),  # 50th anniversary year (2026) is common
        (DOB_TURNS_60_IN_2028, "2026-11"),  # 60th anniversary year (2028) is leap
        (DOB_TURNS_60_IN_2028, "2027-02"),
        ("1964-02-29", "2026-03"),  # 60th anniversary was 2024-02-29 (leap)
        ("1964-02-29", "2027-11"),
        ("1980-02-29", "2026-01"),  # no nearby cutoff; still constructed all of them
        ("1980-02-29", "2027-12"),
    ],
)
def test_employee_ow_cpf_accepts_synthetic_29_feb_dobs(dob, month):
    result = _employee(dob, month)
    assert result["status"] == "bounded_reference"
    assert "worker_share_sgd" in result


@pytest.mark.parametrize(
    "dob,month",
    [
        (DOB_TURNS_50_IN_2026, "2026-02"),
        (DOB_TURNS_50_IN_2026, "2026-03"),
        (DOB_TURNS_50_IN_2026, "2026-04"),
        (DOB_TURNS_55_IN_2027, "2026-11"),
        (DOB_TURNS_60_IN_2028, "2026-06"),
        ("1980-02-29", "2026-01"),
    ],
)
def test_platform_cpf_accepts_synthetic_29_feb_dobs(dob, month):
    result = _platform(dob, month, opted_in=True)
    assert result["status"] == "bounded_reference"
    assert "worker_share_sgd" in result


def test_self_employed_medisave_accepts_synthetic_29_feb_dob():
    # age_on('1976-02-29', 2026-01-01) is 49; this path must not raise either.
    result = self_employed_medisave_2026(
        dob=DOB_TURNS_50_IN_2026,
        annual_nti="12000",
        non_pensioner=True,
        platform_earnings_excluded=True,
    )
    assert result["status"] == "bounded_reference"
    assert result["age_at_jan1"] == 49
    assert result["annual_medisave_reference_sgd"] == "600.00"


def test_employee_29_feb_band_changes_in_april_when_attained_on_1_mar_common_year():
    """1972-02-29 attains 55 on 1 Mar 2027; rates change in the following month."""
    def rates(month):
        result = _employee(DOB_TURNS_55_IN_2027, f"2027-{month:02d}")
        assert result["status"] == "bounded_reference"
        return result["employer_rate_pct"], result["worker_rate_pct"]

    assert rates(2) == ("17", "20")
    assert rates(3) == ("17", "20")
    assert rates(4) == ("16.5", "19")


def test_platform_29_feb_band_changes_in_april_when_attained_on_1_mar_common_year():
    """1976-02-29 attains 50 on 1 Mar 2026; opted-in worker rate 15 → 15.5 in April."""
    def rate(month):
        result = _platform(DOB_TURNS_50_IN_2026, f"2026-{month:02d}", opted_in=True)
        assert result["status"] == "bounded_reference"
        return result["worker_rate_pct"]

    assert rate(2) == "15"
    assert rate(3) == "15"
    assert rate(4) == "15.5"


def test_band_index_29_feb_common_year_uses_march_as_birthday_month():
    # 55th attained-age date is 2027-03-01, so March still uses the prior band.
    assert _band_index(DOB_TURNS_55_IN_2027, 2027, 2, EMPLOYEE_CUTOFFS) == 0
    assert _band_index(DOB_TURNS_55_IN_2027, 2027, 3, EMPLOYEE_CUTOFFS) == 0
    assert _band_index(DOB_TURNS_55_IN_2027, 2027, 4, EMPLOYEE_CUTOFFS) == 1


def test_band_index_29_feb_leap_year_uses_february_as_birthday_month():
    # 60th attained-age date is 2028-02-29, so the band changes in March.
    assert _band_index(DOB_TURNS_60_IN_2028, 2028, 2, EMPLOYEE_CUTOFFS) == 1
    assert _band_index(DOB_TURNS_60_IN_2028, 2028, 3, EMPLOYEE_CUTOFFS) == 2
    assert _band_index(DOB_TURNS_60_IN_2028, 2028, 4, EMPLOYEE_CUTOFFS) == 2


def test_band_index_29_feb_leap_year_platform_cutoffs():
    # Same leap-year 60th birthday, platform cutoff list.
    assert _band_index(DOB_TURNS_60_IN_2028, 2028, 2, PLATFORM_CUTOFFS) == 4
    assert _band_index(DOB_TURNS_60_IN_2028, 2028, 3, PLATFORM_CUTOFFS) == 5


def test_band_index_29_feb_does_not_raise_across_common_and_leap_anniversaries():
    # Every cutoff anniversary is constructed; at least one is always a common year
    # and at least one nearby 29-Feb cohort has a leap anniversary (1964+60=2024).
    dobs = (DOB_TURNS_55_IN_2027, DOB_TURNS_50_IN_2026, DOB_TURNS_60_IN_2028, "1964-02-29", "1980-02-29")
    years = (2024, 2025, 2026, 2027, 2028)  # 2024 and 2028 leap; 2025-2027 common
    for dob in dobs:
        for year in years:
            for month in range(1, 13):
                idx = _band_index(dob, year, month, EMPLOYEE_CUTOFFS)
                assert 0 <= idx <= len(EMPLOYEE_CUTOFFS)
                idx = _band_index(dob, year, month, PLATFORM_CUTOFFS)
                assert 0 <= idx <= len(PLATFORM_CUTOFFS)


def test_attained_age_dates_agree_with_age_on_for_29_feb():
    """The statutory birthday used for banding must be the first day age_on == age."""
    cases = (
        (DOB_TURNS_55_IN_2027, 55, date(2027, 3, 1), EMPLOYEE_CUTOFFS),
        (DOB_TURNS_50_IN_2026, 50, date(2026, 3, 1), PLATFORM_CUTOFFS),
        (DOB_TURNS_60_IN_2028, 60, date(2028, 2, 29), EMPLOYEE_CUTOFFS),
        ("1964-02-29", 60, date(2024, 2, 29), EMPLOYEE_CUTOFFS),
    )
    for dob, age, expected, cutoffs in cases:
        # Infer the date the band logic treats as the birthday: first of the
        # birthday month is when start <= that date still holds, and the next
        # month is in the following band.
        year = expected.year
        prior = _band_index(dob, year, expected.month, cutoffs)
        following = _band_index(dob, year, expected.month + 1, cutoffs)
        assert following == prior + 1
        assert age_on(dob, expected) == age
        assert age_on(dob, expected - timedelta(days=1)) == age - 1
