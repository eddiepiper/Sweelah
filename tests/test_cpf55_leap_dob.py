"""29-Feb dates of birth must have a 55th-birthday snapshot in transition_at_55.

Synthetic dates only. The 1 March common-year convention below is an
INTERNAL ASSUMPTION aligned with core.age_on; it is not checked against
the CPF Board or any statutory convention (Phase 7 external review skipped).
A 29-Feb person attains the new age on 1 Mar in a common year, and on
29 Feb in a leap year.

A 29-Feb DOB is only valid in a leap year, and 55 ≡ 3 (mod 4), so the
55th anniversary year is never a leap year. The only verified-FRS case
is therefore 1972-02-29 attaining 55 on 2027-03-01. Leap-year behaviour
of the shared attained-age rule is tested via the helper at ages whose
anniversaries do fall on 29 Feb (52, 56, 60).
"""

from datetime import date, timedelta

import pytest

from retirepilot.core import age_on
from retirepilot.cpf_retirement_v26 import CPFUnsupportedCase, transition_at_55

# Valid 29-Feb dates of birth (those years are leap years).
DOB_55_IN_2027_COMMON = "1972-02-29"  # 55th attained-age date: 2027-03-01 (common)
DOB_55_IN_2023_COMMON = "1968-02-29"  # 55th attained-age date: 2023-03-01 (common; no verified FRS)
SNAPSHOT_2027_COMMON = date(2027, 3, 1)
SNAPSHOT_2023_COMMON = date(2023, 3, 1)
# Leap-year attained-age dates for the same people, at ages ≡ 0 (mod 4).
SNAPSHOT_1972_AGE_52_LEAP = date(2024, 2, 29)
SNAPSHOT_1972_AGE_56_LEAP = date(2028, 2, 29)
SNAPSHOT_1968_AGE_56_LEAP = date(2024, 2, 29)
SNAPSHOT_1968_AGE_60_LEAP = date(2028, 2, 29)

# 2026-style balances applied to the 2027 FRS (228200).
BALANCES_2027_FRS = dict(
    oa="100000", sa="160000", ma="50000", cpf_membership_confirmed=True
)
# Existing 2027 SA-excess contract balances.
BALANCES_2027_EXCESS = dict(
    oa="1000", sa="250000", ma="20000", cpf_membership_confirmed=True
)
# Existing 2026 contract balances, for ordinary-DOB regressions only.
BALANCES_2026 = dict(
    oa="100000", sa="160000", ma="50000", cpf_membership_confirmed=True
)


def test_age_on_29_feb_attains_55_on_1_mar_in_common_year():
    assert SNAPSHOT_2027_COMMON.year % 4 != 0
    assert SNAPSHOT_2023_COMMON.year % 4 != 0
    assert age_on(DOB_55_IN_2027_COMMON, date(2027, 2, 28)) == 54
    assert age_on(DOB_55_IN_2027_COMMON, SNAPSHOT_2027_COMMON) == 55
    assert age_on(DOB_55_IN_2023_COMMON, date(2023, 2, 28)) == 54
    assert age_on(DOB_55_IN_2023_COMMON, SNAPSHOT_2023_COMMON) == 55


def test_age_on_29_feb_attains_new_age_on_29_feb_in_leap_year():
    assert SNAPSHOT_1972_AGE_52_LEAP == date(2024, 2, 29)
    assert SNAPSHOT_1972_AGE_56_LEAP == date(2028, 2, 29)
    assert age_on(DOB_55_IN_2027_COMMON, date(2024, 2, 28)) == 51
    assert age_on(DOB_55_IN_2027_COMMON, SNAPSHOT_1972_AGE_52_LEAP) == 52
    assert age_on(DOB_55_IN_2027_COMMON, date(2024, 3, 1)) == 52
    assert age_on(DOB_55_IN_2027_COMMON, date(2028, 2, 28)) == 55
    assert age_on(DOB_55_IN_2027_COMMON, SNAPSHOT_1972_AGE_56_LEAP) == 56
    assert age_on(DOB_55_IN_2027_COMMON, date(2028, 3, 1)) == 56
    assert age_on(DOB_55_IN_2023_COMMON, SNAPSHOT_1968_AGE_56_LEAP) == 56
    assert age_on(DOB_55_IN_2023_COMMON, SNAPSHOT_1968_AGE_60_LEAP) == 60


def test_transition_29_feb_common_year_2027_uses_1_mar_snapshot():
    result = transition_at_55(
        dob=DOB_55_IN_2027_COMMON, as_of="2027-03-01", **BALANCES_2027_FRS
    )
    assert result["event_date"] == "2027-03-01"
    assert result["frs_cohort_year"] == 2027
    assert result["frs"] == "228200"
    assert result["transfers"]["SA_to_RA"] == "160000"
    assert result["transfers"]["OA_to_RA"] == "68200"
    assert result["transfers"]["SA_to_OA_excess"] == "0"
    assert result["closing"] == {
        "OA": "31800",
        "SA": "0",
        "MA": "50000",
        "RA": "228200",
    }
    assert result["below_FRS"] is False
    assert result["status"] == "bounded_reference"


def test_transition_29_feb_common_year_2027_sa_excess_and_below_frs():
    excess = transition_at_55(
        dob=DOB_55_IN_2027_COMMON, as_of="2027-03-01", **BALANCES_2027_EXCESS
    )
    assert excess["event_date"] == "2027-03-01"
    assert excess["frs"] == "228200"
    assert excess["transfers"]["SA_to_OA_excess"] == "21800"
    assert excess["closing"]["OA"] == "22800"
    assert excess["closing"]["SA"] == "0"
    assert excess["closing"]["RA"] == "228200"
    assert excess["below_FRS"] is False

    short = transition_at_55(
        dob=DOB_55_IN_2027_COMMON,
        as_of="2027-03-01",
        oa="10000",
        sa="15000",
        ma="0",
        cpf_membership_confirmed=True,
    )
    assert short["event_date"] == "2027-03-01"
    assert short["closing"]["RA"] == "25000"
    assert short["below_FRS"] is True


def test_transition_29_feb_common_year_adjacent_days_still_rejected():
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2027_COMMON, as_of="2027-02-28", **BALANCES_2027_FRS
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2027_COMMON, as_of="2027-03-02", **BALANCES_2027_FRS
        )


def test_transition_29_feb_common_year_nonexistent_29_feb_as_of_is_invalid_date():
    with pytest.raises(CPFUnsupportedCase, match="Valid ISO date"):
        transition_at_55(
            dob=DOB_55_IN_2027_COMMON, as_of="2027-02-29", **BALANCES_2027_FRS
        )


def test_transition_29_feb_55th_in_unsupported_cohort_is_frs_limit_not_birthday():
    """1968-02-29 attains 55 on 2023-03-01 (also a common year).

    After the date check accepts 1 Mar, the remaining refusal is the
    existing 2026/27 FRS cohort limitation — a genuine unsupported case.
    """
    with pytest.raises(CPFUnsupportedCase, match="Only 2026 and 2027"):
        transition_at_55(
            dob=DOB_55_IN_2023_COMMON, as_of="2023-03-01", **BALANCES_2026
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2023_COMMON, as_of="2023-02-28", **BALANCES_2026
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2023_COMMON, as_of="2023-03-02", **BALANCES_2026
        )


def test_transition_29_feb_leap_year_date_is_not_the_55th_snapshot():
    """A 29-Feb person's 55th anniversary cannot fall in a leap year.

    2024-02-29 and 2028-02-29 are real leap-day dates, but they are the
    52nd/56th (1972) or 56th/60th (1968) attained-age dates, so the
    55th-birthday snapshot must still be refused.
    """
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2027_COMMON, as_of="2024-02-29", **BALANCES_2027_FRS
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2027_COMMON, as_of="2028-02-29", **BALANCES_2027_FRS
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2023_COMMON, as_of="2024-02-29", **BALANCES_2026
        )
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(
            dob=DOB_55_IN_2023_COMMON, as_of="2028-02-29", **BALANCES_2026
        )


def test_ordinary_june_dob_snapshot_unchanged():
    result = transition_at_55(
        dob="1971-06-01", as_of="2026-06-01", **BALANCES_2026
    )
    assert result["event_date"] == "2026-06-01"
    assert result["frs"] == "220400"
    assert result["transfers"]["SA_to_RA"] == "160000"
    assert result["transfers"]["OA_to_RA"] == "60400"
    assert result["closing"] == {
        "OA": "39600",
        "SA": "0",
        "MA": "50000",
        "RA": "220400",
    }
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(dob="1971-06-01", as_of="2026-05-31", **BALANCES_2026)
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(dob="1971-06-01", as_of="2026-06-02", **BALANCES_2026)


def test_ordinary_1_mar_and_28_feb_dobs_unchanged():
    march = transition_at_55(
        dob="1971-03-01", as_of="2026-03-01", **BALANCES_2026
    )
    assert march["event_date"] == "2026-03-01"
    assert march["closing"]["RA"] == "220400"
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(dob="1971-03-01", as_of="2026-02-28", **BALANCES_2026)

    feb28 = transition_at_55(
        dob="1971-02-28", as_of="2026-02-28", **BALANCES_2026
    )
    assert feb28["event_date"] == "2026-02-28"
    assert feb28["closing"]["RA"] == "220400"
    with pytest.raises(CPFUnsupportedCase, match="exact 55th-birthday"):
        transition_at_55(dob="1971-02-28", as_of="2026-03-01", **BALANCES_2026)


def test_ordinary_2027_january_dob_unchanged():
    result = transition_at_55(
        dob="1972-01-01", as_of="2027-01-01", **BALANCES_2027_EXCESS
    )
    assert result["event_date"] == "2027-01-01"
    assert result["frs"] == "228200"
    assert result["transfers"]["SA_to_OA_excess"] == "21800"
    assert result["closing"]["OA"] == "22800"


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            dob=DOB_55_IN_2027_COMMON,
            as_of="2027-03-01",
            oa="100000",
            sa="160000",
            ma="50000",
        ),
        dict(
            dob=DOB_55_IN_2027_COMMON,
            as_of="2027-03-01",
            oa="100000",
            sa="160000",
            ma="50000",
            existing_ra="5",
            cpf_membership_confirmed=True,
        ),
        dict(
            dob=DOB_55_IN_2027_COMMON,
            as_of="2027-03-01",
            oa="100000",
            sa="160000",
            ma="50000",
            cpf_membership_confirmed=True,
            property_pledge=True,
        ),
        dict(
            dob=DOB_55_IN_2027_COMMON,
            as_of="2027-03-01",
            oa="nan",
            sa="160000",
            ma="50000",
            cpf_membership_confirmed=True,
        ),
        dict(
            dob="not-a-date",
            as_of="2027-03-01",
            oa="100000",
            sa="160000",
            ma="50000",
            cpf_membership_confirmed=True,
        ),
        dict(
            dob="1970-03-01",
            as_of="2025-03-01",
            oa="100000",
            sa="160000",
            ma="50000",
            cpf_membership_confirmed=True,
        ),
    ],
)
def test_other_unsupported_cases_still_raise(kwargs):
    with pytest.raises(CPFUnsupportedCase):
        transition_at_55(**kwargs)


def test_attained_age_date_helper_matches_age_on_common_and_leap_years():
    from retirepilot.cpf_retirement_v26 import _attained_age_date

    cases = [
        (DOB_55_IN_2027_COMMON, 55, SNAPSHOT_2027_COMMON),
        (DOB_55_IN_2023_COMMON, 55, SNAPSHOT_2023_COMMON),
        (DOB_55_IN_2027_COMMON, 52, SNAPSHOT_1972_AGE_52_LEAP),
        (DOB_55_IN_2027_COMMON, 56, SNAPSHOT_1972_AGE_56_LEAP),
        (DOB_55_IN_2023_COMMON, 56, SNAPSHOT_1968_AGE_56_LEAP),
        (DOB_55_IN_2023_COMMON, 60, SNAPSHOT_1968_AGE_60_LEAP),
        ("1971-06-01", 55, date(2026, 6, 1)),
        ("1971-03-01", 55, date(2026, 3, 1)),
        ("1971-02-28", 55, date(2026, 2, 28)),
        ("1972-01-01", 55, date(2027, 1, 1)),
    ]
    for dob, age, snapshot in cases:
        assert _attained_age_date(date.fromisoformat(dob), age) == snapshot
        assert age_on(dob, snapshot) == age
        assert age_on(dob, snapshot - timedelta(days=1)) == age - 1

def test_attained_age_date_refuses_calendar_year_past_9999():
    """Years past datetime.date's 9999 limit must be a controlled refusal.

    Synthetic far-future dates only. date(year+age, ...) raises a bare
    ValueError once the result year exceeds 9999; that must not leak out
    of the helper. 9945-02-29 is not a real date (9945 is not a leap year).
    """
    from retirepilot.cpf_retirement_v26 import CPFUnsupportedCase, _attained_age_date

    # 9950-01-15 + 55 = year 10005, past the calendar limit.
    with pytest.raises(CPFUnsupportedCase, match="outside the supported date range") as exc:
        _attained_age_date(date(9950, 1, 15), 55)
    assert type(exc.value) is CPFUnsupportedCase

    # 9944-02-29 is a real leap-day DOB near the limit; age 56 lands on year 10000.
    with pytest.raises(CPFUnsupportedCase, match="outside the supported date range") as exc:
        _attained_age_date(date(9944, 2, 29), 56)
    assert type(exc.value) is CPFUnsupportedCase


def test_attained_age_date_9944_feb29_age_55_still_falls_on_1_mar_of_9999():
    """The last in-range 29-Feb / age-55 anniversary still uses the 1-Mar rule."""
    from retirepilot.cpf_retirement_v26 import _attained_age_date

    # 9944 + 55 = 9999, a common year, so the attained-age date is 9999-03-01.
    assert _attained_age_date(date(9944, 2, 29), 55) == date(9999, 3, 1)


def test_transition_at_55_refuses_dob_whose_55th_year_exceeds_9999():
    """Callers of transition_at_55 must see CPFUnsupportedCase, not ValueError."""
    kwargs = dict(
        oa="100000",
        sa="160000",
        ma="50000",
        cpf_membership_confirmed=True,
    )
    with pytest.raises(CPFUnsupportedCase, match="outside the supported date range") as exc:
        transition_at_55(dob="9950-01-15", as_of="2027-01-15", **kwargs)
    assert type(exc.value) is CPFUnsupportedCase

    # Leap-day DOB whose age-55 year is already past 9999 (9948+55=10003).
    with pytest.raises(CPFUnsupportedCase, match="outside the supported date range") as exc:
        transition_at_55(dob="9948-02-29", as_of="2027-03-01", **kwargs)
    assert type(exc.value) is CPFUnsupportedCase
