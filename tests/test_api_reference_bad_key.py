"""SWEELAH-API-REF-KEY: a wrong or unknown key on POST /api/reference must be 422, not 500.

On main 5fe3ec8, several bad inputs made FastAPI return 500:
- `kind` as a list or object (unhashable; TypeError before the handler's try/except)
- a non-object JSON body (AttributeError on data.get)
- a missing `month` / `ordinary_wages` key inside employee_cpf_schedule items (KeyError,
  which the handler did not catch)

Unexpected or empty param keys already returned 422, but the detail echoed the submitted
key and the internal function name. The message must be controlled and must not echo
arbitrary input. ValidationError details from the reference functions stay as they are.
Synthetic fixtures only.
"""
import pytest
from fastapi.testclient import TestClient

from retirepilot.api import app

CLIENT = TestClient(app, raise_server_exceptions=False)
SID = 'RP-SYNTH-001'
UNSUPPORTED = 'Unsupported reference calculation'
BAD_PARAMS = 'Invalid reference parameters'
NOT_OBJECT = 'request must be an object'
PARAMS_OBJECT = 'params must be object'
PROBE = 'LEAK-ME-KEY-9f3c2a1b'


def post(payload):
    return CLIENT.post('/api/reference', json=payload)


def ref(**extra):
    body = {'synthetic_profile_id': SID}
    body.update(extra)
    return body


def tax_params(**extra):
    params = {
        'chargeable_income': '120000',
        'year_of_assessment': 2026,
        'resident_confirmed': True,
        'chargeable_income_confirmed': True,
    }
    params.update(extra)
    return params


def schedule_params(items):
    return {
        'dob': '1970-01-15',
        'residency': 'citizen',
        'pr_cpf_year': None,
        'months_and_wages': items,
    }


def assert_422(response, detail):
    assert response.status_code == 422, response.text
    assert response.json() == {'detail': detail}
    assert PROBE not in response.text
    # Internal implementation names must not leak into the client message.
    assert 'resident_tax_reference' not in response.text
    assert 'employee_cpf_schedule' not in response.text


def test_unknown_kind_is_controlled_422():
    assert_422(post(ref(kind=PROBE, params={})), UNSUPPORTED)


def test_missing_kind_is_controlled_422():
    assert_422(post(ref(params={})), UNSUPPORTED)


def test_empty_string_kind_is_controlled_422():
    assert_422(post(ref(kind='', params={})), UNSUPPORTED)


def test_kind_list_is_controlled_422_not_500():
    assert_422(post(ref(kind=['resident_tax'], params={})), UNSUPPORTED)


def test_kind_object_is_controlled_422_not_500():
    assert_422(post(ref(kind={'name': 'resident_tax'}, params={})), UNSUPPORTED)


def test_unknown_params_key_is_controlled_422_and_does_not_echo():
    assert_422(post(ref(kind='resident_tax', params={PROBE: 1})), BAD_PARAMS)


def test_empty_string_params_key_is_controlled_422_and_does_not_echo():
    assert_422(post(ref(kind='resident_tax', params={'': 1})), BAD_PARAMS)


def test_missing_required_params_is_controlled_422():
    assert_422(post(ref(kind='resident_tax', params={})), BAD_PARAMS)


def test_missing_schedule_item_key_is_controlled_422_not_500():
    assert_422(
        post(ref(kind='employee_cpf_schedule', params=schedule_params([{'ordinary_wages': '3000'}]))),
        BAD_PARAMS,
    )


def test_schedule_item_with_only_unknown_key_is_controlled_422_not_500():
    assert_422(
        post(ref(kind='employee_cpf_schedule', params=schedule_params([{PROBE: '2026-01'}]))),
        BAD_PARAMS,
    )


@pytest.mark.parametrize('payload', ['[]', '"hello"', 'null', '1', 'true'])
def test_non_object_bodies_are_controlled_422_not_500(payload):
    response = CLIENT.post('/api/reference', content=payload)
    assert response.status_code == 422, response.text
    assert response.json() == {'detail': NOT_OBJECT}


def test_params_wrong_type_keeps_existing_message():
    assert_422(post(ref(kind='resident_tax', params='nope')), PARAMS_OBJECT)
    assert_422(post(ref(kind='resident_tax', params=[])), PARAMS_OBJECT)
    assert_422(post(ref(kind='resident_tax')), PARAMS_OBJECT)


def test_unknown_cpf_account_key_keeps_validation_message():
    response = post(ref(
        kind='cpf_interest_static',
        params={
            'age': 40,
            'balances': {'XX': '1000'},
            'as_of_quarter': '2026Q4',
            'no_transactions_confirmed': True,
        },
    ))
    assert response.status_code == 422, response.text
    assert response.json() == {'detail': 'Invalid CPF account list'}


def test_valid_resident_tax_reference_still_returns_bounded_result():
    response = post(ref(kind='resident_tax', params=tax_params()))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['status'] == 'bounded_reference'
    assert body['tax_before_rebates_sgd'] == '7950.00'
