"""SWEELAH-ISSUE-8 (Refs #8): every catalogue entry is mapped, the 26 new
mappings are labelled INTERNAL_UNVALIDATED, and no reference dangles."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from retirepilot.catalog_scenarios_v26 import compile_catalog_scenario
from retirepilot.core import ValidationError
from retirepilot.priority_scenarios_v27 import PRIORITY_IDS
from retirepilot.scenario_mapping_internal import (
    INTERNAL_LABEL, MAPPING_PATH, V26_REGISTRY_PATH, coverage_matrix, internal_mapping,
    reference_errors, v26_registry)

ROOT = Path(__file__).resolve().parent.parent
PROFILE = json.loads((ROOT / 'data/mixed_income_household.json').read_text())
FORMERLY_UNMAPPED = sorted(r['id'] for r in v26_registry() if r['previous_status'] == 'UNMAPPED')
RESEARCH = {s['ID']: s for s in json.loads(
    (ROOT / 'research/retirepilot_2026_11_04/scenario_engine_contracts_46.json').read_text())}


def _entry(sid):
    return next(m for m in internal_mapping()['entries'] if m['id'] == sid)


def test_count_of_formerly_unmapped_entries_is_26():
    assert len(v26_registry()) == 46
    assert len(FORMERLY_UNMAPPED) == 26


def test_every_catalogue_entry_is_mapped():
    unmapped = [r['id'] for r in coverage_matrix() if not r['mapped']]
    assert unmapped == [], f'{len(unmapped)} catalogue entries still unmapped: {unmapped}'


def test_internal_mapping_covers_exactly_the_formerly_unmapped():
    assert sorted(m['id'] for m in internal_mapping()['entries']) == FORMERLY_UNMAPPED


def test_document_level_label_is_internal_unvalidated():
    doc = internal_mapping()
    assert doc['validation_status'] == INTERNAL_LABEL
    assert doc['external_validation'] is False
    assert doc['synthetic_only'] is True
    assert 'not externally validated' in doc['label'].lower()


@pytest.mark.parametrize('sid', FORMERLY_UNMAPPED)
def test_each_new_mapping_is_labelled_internal_unvalidated(sid):
    m = _entry(sid)
    assert m['validation_status'] == INTERNAL_LABEL
    assert m['external_validation'] is False
    assert m['coverage']['mapped'] is True
    assert m['coverage']['golden_tested'] is False
    assert m['coverage']['domain_approved'] is False
    assert m['mapped_by'] == 'Engineering Lead (in-house)'
    assert len(m['rationale'].strip()) >= 40
    for key in ('semantic_scope', 'guardrail', 'missing_data_behaviour', 'timing_rule'):
        assert m[key].strip(), key
    assert m['required_facts'] and m['financial_engines'] and m['applicable_decisions']


def test_no_dangling_references():
    assert reference_errors() == []


def test_reference_checker_detects_each_dangling_kind():
    doc = copy.deepcopy(internal_mapping())
    first = doc['entries'][0]
    first['financial_engines'] = first['financial_engines'] + ['F99']
    first['applicable_decisions'] = first['applicable_decisions'] + ['D99']
    first['incompatible_with'] = first['incompatible_with'] + ['S099']
    first['component_tests'] = first['component_tests'] + ['tests/test_nope.py::test_missing']
    first['v26_name'] = 'renamed'
    doc['entries'].append({'id': 'S999'})
    errors = '\n'.join(reference_errors(doc))
    for needle in ('F99', 'D99', 'S099', 'test_missing', 'v26_name', 'S999'):
        assert needle in errors


@pytest.mark.parametrize('sid', FORMERLY_UNMAPPED)
def test_mapping_follows_research_contract_and_registry(sid):
    m, spec = _entry(sid), RESEARCH[sid]
    assert m['financial_engines'] == spec['Financial engines'].split(',')
    assert m['required_facts'] == [x.strip() for x in spec['Required facts'].split(';')]
    assert m['guardrail'] == spec['Guardrail / refusal']


FAIL_CLOSED = sorted(r['id'] for r in v26_registry() if r['previous_status'] == 'UNMAPPED'
                     and r['execution_strategy'] == 'NOT_SAFE_TO_COMPILE' and r['id'] not in PRIORITY_IDS)


@pytest.mark.parametrize('sid', FAIL_CLOSED)
def test_unsupported_entries_do_not_imply_an_effect(sid):
    assert _entry(sid)['coverage']['implemented'] == 'NOT_IMPLEMENTED_FAIL_CLOSED'
    with pytest.raises(ValidationError, match='requires an unimplemented'):
        compile_catalog_scenario(PROFILE, sid, {})


def test_coverage_matrix_separates_levels_honestly():
    rows = coverage_matrix()
    assert len(rows) == 46
    assert Counter(r['implemented'] for r in rows) == {
        'PREEXISTING_BOUNDED_OPERATOR': 20, 'LIMITED_COMPONENT': 7, 'LIMITED_PREVIEW': 2,
        'BLOCKED_PREVIEW': 1, 'NOT_IMPLEMENTED_FAIL_CLOSED': 16}
    assert not any(r['golden_tested'] or r['domain_approved'] for r in rows)
    assert sum(r['validation_status'] == INTERNAL_LABEL for r in rows) == 26


def test_no_external_validation_claims_in_mapping_text():
    text = MAPPING_PATH.read_text(encoding='utf-8').lower()
    for phrase in ('externally validated by', 'signed off by', 'domain-approved by', 'certified',
                   'production-ready', 'approved by expert'):
        assert phrase not in text, phrase


def test_runtime_registry_untouched_by_issue8():
    manifest = json.loads((ROOT / 'docs_v26/VERIFICATION_MANIFEST_v26.json').read_text())
    expected = manifest['files']['data/scenario_contracts_v26.json']
    assert hashlib.sha256(V26_REGISTRY_PATH.read_bytes()).hexdigest() == expected
