"""S016 bounded preview contracts; all inputs are synthetic."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from retirepilot.api import app
from retirepilot.core import ValidationError
from retirepilot.priority_scenarios_v27 import preview_priority_scenario, PRIORITY_STATUS

ROOT = Path(__file__).resolve().parents[1]
CLIENT = TestClient(app)
ROUTE = '/api/scenarios/S016/preview'
VALID = {'additional_care_cost_monthly': '1200', 'months': 12}
INVALID = [
    {}, {'months': 12}, {'additional_care_cost_monthly': '1200'},
    *[dict(VALID, additional_care_cost_monthly=v) for v in [0, -1, None, True, '', 'no', 'NaN', 'Infinity']],
    *[dict(VALID, months=v) for v in [0, 121, 1.5, 1.0, True, False, '12', None]],
]


def payload(params):
    return {'synthetic_profile_id': 'RP-SYNTH-S016', 'params': params}


@pytest.mark.parametrize('params', INVALID)
def test_unit_refuses_invalid_s016(params):
    with pytest.raises(ValidationError):
        preview_priority_scenario('S016', params)


@pytest.mark.parametrize('months', [1, 120])
def test_unit_s016_duration_boundaries_and_decimal_cost(months):
    result = preview_priority_scenario('S016', {'additional_care_cost_monthly': '12.50', 'months': months})
    assert result['extra_monthly_cost'] == '12.50'
    assert result['period_cash_cost'] == f'{12.5 * months:.2f}'
    assert result['may_post_to_household_projection'] is False


@pytest.mark.parametrize('params', INVALID)
def test_api_refuses_invalid_s016(params):
    response = CLIENT.post(ROUTE, json=payload(params))
    assert response.status_code == 422
    assert response.json()['detail']
    assert 'period_cash_cost' not in response.json()


@pytest.mark.parametrize('params,monthly,total', [
    (VALID, '1200.00', '14400.00'),
    ({'additional_care_cost_monthly': 12.50, 'months': 1}, '12.50', '12.50'),
    ({'additional_care_cost_monthly': '12.50', 'months': 120}, '12.50', '1500.00'),
])
def test_api_s016_preview_contract(params, monthly, total):
    response = CLIENT.post(ROUTE, json=payload(params))
    assert response.status_code == 200
    result = response.json()
    assert result['extra_monthly_cost'] == monthly
    assert result['months'] == params['months']
    assert result['period_cash_cost'] == total
    assert result['meaning'] == preview_priority_scenario('S016', params)['meaning']
    assert result['status'] == PRIORITY_STATUS['S016'][1] == 'LIMITED_RECURRING_COST_PREVIEW_ONLY'
    assert result['implemented_as'] == 'bounded_preview_not_full_event'
    assert result['may_post_to_household_projection'] is False
    assert result['synthetic_only'] is True
    assert 'synthetic' in result['label'].lower()
    for limitation in ['subsidy', 'insurance', 'wage loss', 'entitlement', 'no inflation']:
        assert limitation in ' '.join(result['limitations']).lower()


@pytest.mark.parametrize('body', [None, [], 'text', 12, True])
def test_api_rejects_non_object_envelopes(body):
    assert CLIENT.post(ROUTE, content=json.dumps(body)).status_code == 422


@pytest.mark.parametrize('params', [None, [], 'text', True])
def test_api_rejects_non_object_params(params):
    assert CLIENT.post(ROUTE, json=payload(params)).status_code == 422


@pytest.mark.parametrize('identifier', ['', 'REAL-USER', None])
def test_api_synthetic_gate(identifier):
    data = payload(VALID)
    data['synthetic_profile_id'] = identifier
    assert CLIENT.post(ROUTE, json=data).status_code == 403


def test_api_missing_identity_and_malformed_json():
    assert CLIENT.post(ROUTE, json={'params': VALID}).status_code == 403
    assert CLIENT.post(ROUTE, content='{').status_code == 400


def test_api_zero_cost_clear_positive_only_copy():
    response = CLIENT.post(ROUTE, json=payload(dict(VALID, additional_care_cost_monthly=0)))
    assert 'must be more than 0' in response.json()['detail']


def test_api_unrepresentable_cost_refused_not_500():
    assert CLIENT.post(ROUTE, json=payload(dict(VALID, additional_care_cost_monthly='1e99999'))).status_code == 422


def test_preview_does_not_mutate_household_projection():
    profile = CLIENT.get('/api/sample').json()
    before = CLIENT.post('/api/evaluate', json={'profile': profile, 'years': 2}).json()
    assert CLIENT.post(ROUTE, json=payload(VALID)).status_code == 200
    after = CLIENT.post('/api/evaluate', json={'profile': profile, 'years': 2}).json()
    assert before == after


def test_registry_and_ui_remain_preview_only():
    registry = json.loads((ROOT / 'data/scenario_contracts_v26.json').read_text())
    assert next(row for row in registry if row['id'] == 'S016')['implemented_component'] is False
    response = CLIENT.get('/sweelah')
    assert response.status_code == 200
    assert 'Parent-care cost preview' in response.text
    assert 'preview' in (ROOT / 'retirepilot/S016_README.md').read_text().lower()


PRECISION_ERROR = 'Enter an amount with up to 2 decimal places, for example 1200.50.'


@pytest.mark.parametrize('cost', ['1.005', 1.005, '0.0001', '1.500', '1e-3', '1.005e0'])
def test_api_subcent_cost_refused_before_preview(monkeypatch, cost):
    def forbidden_preview(*args):
        pytest.fail('precision-invalid input reached preview_priority_scenario')
    monkeypatch.setattr('retirepilot.api.preview_priority_scenario', forbidden_preview)
    response = CLIENT.post(ROUTE, json=payload(dict(VALID, additional_care_cost_monthly=cost)))
    assert response.status_code == 422
    assert response.json() == {'detail': PRECISION_ERROR}


@pytest.mark.parametrize('cost,monthly,total', [
    ('1.50', '1.50', '18.00'), (1.5, '1.50', '18.00'),
    ('1,200.5', '1200.50', '14406.00'), ('S$1,200.5', '1200.50', '14406.00'), ('1e2', '100.00', '1200.00'),
    ('1e-2', '0.01', '0.12'), ('1.005e2', '100.50', '1206.00'),
])
def test_api_cents_and_exponent_forms(cost, monthly, total):
    response = CLIENT.post(ROUTE, json=payload(dict(VALID, additional_care_cost_monthly=cost)))
    assert response.status_code == 200
    assert response.json()['extra_monthly_cost'] == monthly
    assert response.json()['period_cash_cost'] == total


def test_api_json_decimal_precision_is_not_lost_to_float():
    response = CLIENT.post(ROUTE, content='{"synthetic_profile_id":"RP-SYNTH-S016","params":{"additional_care_cost_monthly":1.0000000000000001,"months":12}}')
    assert response.status_code == 422
    assert response.json() == {'detail': PRECISION_ERROR}


@pytest.mark.parametrize('cost,accepted', [('1.005', False), ('1.50', True), ('1e2', True), ('1e-3', False)])
def test_endpoint_cost_precision_validator(cost, accepted):
    from retirepilot.api import validate_s016_cost
    if accepted:
        assert validate_s016_cost(cost)
    else:
        with pytest.raises(ValidationError, match='up to 2 decimal places'):
            validate_s016_cost(cost)


def test_api_unrepresentable_json_exponent_refused_not_500():
    response = CLIENT.post(ROUTE, content='{"synthetic_profile_id":"RP-SYNTH-S016","params":{"additional_care_cost_monthly":1e99999999999999999999999,"months":12}}')
    assert response.status_code == 422
    assert set(response.json()) == {'detail'}
