"""SWEELAH-ATTAIN-CORE: one attained-age helper in core, plus a year cap for
projection_v22._anniversary (synthetic data only).

The ``_OLD_*`` functions below are verbatim copies of the three implementations
on main 5fe3ec8 (statutory_2026._attained_age_date,
cpf_retirement_v26._attained_age_date and projection_v22._anniversary). They are
frozen oracles: the consolidated helper must give the same date wherever the old
code returned a date, and the same exception type and message wherever the old
statutory/CPF code raised.

INTERNAL ASSUMPTION (unchanged, not checked against the CPF Board or any statutory
convention; Phase 7 external review skipped): a 29-Feb person attains the new age
on 1 Mar in a common year, matching core.age_on.
"""
from calendar import monthrange
from datetime import date

import pytest
from fastapi.testclient import TestClient

from retirepilot import core
from retirepilot.core import ValidationError, age_on, project
from retirepilot import statutory_2026, cpf_retirement_v26, projection_v22
from retirepilot.cpf_retirement_v26 import CPFUnsupportedCase


# --- Frozen oracles: verbatim logic from main 5fe3ec8 ------------------------------

def _OLD_statutory(born, age):
    year = born.year + age
    if year < date.min.year or year > date.max.year:
        raise ValidationError(
            'Attained-age calendar year is outside the supported date range '
            f'({date.min.year}-{date.max.year})'
        )
    try:
        return date(year, born.month, born.day)
    except ValueError:
        return date(year, 3, 1)


def _OLD_cpf(born, age):
    year = born.year + age
    if year < date.min.year or year > date.max.year:
        raise CPFUnsupportedCase(
            'Attained-age calendar year is outside the supported date range '
            f'({date.min.year}-{date.max.year})'
        )
    try:
        return date(year, born.month, born.day)
    except ValueError:
        return date(year, 3, 1)


def _OLD_projection(dob, age):
    d = date.fromisoformat(dob)
    year = d.year + age
    if d.day > monthrange(year, d.month)[1]: return date(year, d.month + 1, 1)
    return date(year, d.month, d.day)


# --- Synthetic sweep: normal DOBs, 29-Feb DOBs, boundary years --------------------

DOBS = [date(y, m, d) for y in (1, 4, 1900, 1944, 1952, 1960, 1964, 1971, 1999, 2000, 2024, 9944, 9945, 9950, 9999)
        for (m, d) in ((1, 1), (2, 28), (3, 1), (5, 20), (5, 31), (12, 31))]
DOBS += [date(y, 2, 29) for y in (4, 1896, 1904, 1944, 1952, 1960, 1964, 1972, 2000, 2024, 9940, 9944, 9996)]
AGES = [-2001, -2000, -1, 0, 1, 3, 4, 45, 55, 56, 59, 60, 65, 70, 95, 96, 100, 110, 9998, 9999, 10000]


def _outcome(fn, *args, **kwargs):
    try:
        return ('date', fn(*args, **kwargs))
    except Exception as exc:  # noqa: BLE001 - recording the exact type is the point
        return ('raise', type(exc), str(exc))


def test_core_helper_exists_and_keeps_1_mar_internal_assumption():
    assert core.attained_age_date(date(1964, 2, 29), 62) == date(2026, 3, 1)
    assert core.attained_age_date(date(1964, 2, 29), 64) == date(2028, 2, 29)
    assert core.attained_age_date(date(1971, 5, 20), 55) == date(2026, 5, 20)


def test_core_helper_default_error_is_validation_error_and_error_is_parameterised():
    with pytest.raises(ValidationError, match='outside the supported date range'):
        core.attained_age_date(date(9950, 1, 15), 55)
    with pytest.raises(CPFUnsupportedCase, match='outside the supported date range'):
        core.attained_age_date(date(9950, 1, 15), 55, error=CPFUnsupportedCase)


@pytest.mark.parametrize('born', DOBS, ids=str)
def test_core_helper_matches_old_statutory_and_cpf_copies(born):
    for age in AGES:
        assert _outcome(core.attained_age_date, born, age) == _outcome(_OLD_statutory, born, age), (born, age)
        assert _outcome(core.attained_age_date, born, age, error=CPFUnsupportedCase) == _outcome(_OLD_cpf, born, age), (born, age)


@pytest.mark.parametrize('born', DOBS, ids=str)
def test_module_wrappers_keep_their_public_exception_types(born):
    for age in AGES:
        assert _outcome(statutory_2026._attained_age_date, born, age) == _outcome(_OLD_statutory, born, age), (born, age)
        assert _outcome(cpf_retirement_v26._attained_age_date, born, age) == _outcome(_OLD_cpf, born, age), (born, age)


def test_modules_route_through_the_single_core_helper(monkeypatch):
    calls = []
    real = core.attained_age_date

    def spy(born, age, **kw):
        calls.append((born, age, kw.get('error', ValidationError)))
        return real(born, age, **kw)

    monkeypatch.setattr(core, 'attained_age_date', spy)
    statutory_2026._attained_age_date(date(1964, 2, 29), 55)
    cpf_retirement_v26._attained_age_date(date(1964, 2, 29), 55)
    projection_v22._anniversary('1964-02-29', 55)
    assert [c[2] for c in calls] == [ValidationError, CPFUnsupportedCase, ValidationError]


@pytest.mark.parametrize('born', DOBS, ids=str)
def test_projection_anniversary_matches_old_copy_wherever_old_copy_returned_a_date(born):
    for age in AGES:
        old = _outcome(_OLD_projection, born.isoformat(), age)
        if old[0] == 'date':
            assert projection_v22._anniversary(born.isoformat(), age) == old[1], (born, age)
            # and agrees with core.age_on (exclusive boundary)
            assert age_on(born.isoformat(), old[1]) == age


@pytest.mark.parametrize('dob,age', [
    ('9950-01-15', 55),        # year 10005
    ('9944-02-29', 56),        # year 10000; 9945-02-29 never exists either
    ('2000-01-01', -2000),     # year 0
    ('2000-01-01', 10 ** 20),  # previously OverflowError (not a ValueError)
])
def test_projection_anniversary_out_of_range_raises_validation_error(dob, age):
    with pytest.raises(ValidationError, match='outside the supported date range'):
        projection_v22._anniversary(dob, age)


def test_projection_anniversary_9944_feb29_age_55_still_1_mar_9999():
    assert projection_v22._anniversary('9944-02-29', 55) == date(9999, 3, 1)


ZERO_RATES = {'inflation_pct': '0', 'nominal_return_pct': '0', 'cash_yield_pct': '0', 'income_growth_pct': '0'}


def _profile(dob, as_of, end_age, streams=()):
    return {
        'id': 'RP-SYNTH-ATTAIN', 'as_of': as_of, 'currency': 'SGD', 'primary_id': 'P1',
        'persons': [{'id': 'P1', 'role': 'primary', 'dob': dob, 'residency': 'SG', 'marital_status': 'single'}],
        'relationships': [], 'income_streams': list(streams), 'expenses': [], 'liabilities': [],
        'assets': [{'id': 'A1', 'type': 'cash', 'owners': {'P1': '1'}, 'value': '1000', 'accessible': True}],
        'goal': {'projection_end_age': end_age}, 'assumptions': dict(ZERO_RATES),
    }


def _stream(**extra):
    return {'id': 'I1', 'owner_id': 'P1', 'type': 'rental', 'gross_monthly': '100', 'worker_cpf_monthly': '0',
            'tax_reserve_monthly': '0', 'cash_deductions_monthly': '0', 'operating_costs_monthly': '0', **extra}


def test_project_horizon_past_9999_is_a_validation_error():
    with pytest.raises(ValidationError, match='outside the supported date range'):
        project(_profile('9950-01-15', '9990-06-01', 95))


def test_project_huge_stream_age_is_a_validation_error_not_overflow():
    with pytest.raises(ValidationError, match='outside the supported date range'):
        project(_profile('1974-05-20', '2027-01-01', 60, [_stream(starts_age=10 ** 20)]))


def test_api_evaluate_huge_stream_age_maps_to_422_not_500():
    from retirepilot.api import app
    client = TestClient(app, raise_server_exceptions=False)
    profile = _profile('1974-05-20', '2027-01-01', 60, [_stream(starts_age=10 ** 20)])
    profile['expenses'] = [{'id': 'E1', 'category': 'other', 'amount_monthly': '50'}]
    body = {'profile': profile, 'years': 5}
    resp = client.post('/api/evaluate', json=body)
    assert resp.status_code == 422, resp.text
    assert 'outside the supported date range' in resp.text
