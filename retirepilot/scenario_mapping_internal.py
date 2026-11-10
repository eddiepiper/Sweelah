"""Issue #8: in-house mapping of the 26 formerly unmapped catalogue scenarios.

INTERNAL / UNVALIDATED. Engineering produced these mappings in-house from the
repository's own synthetic research contracts. No external reviewer, domain
expert, regulator or consumer has validated or signed off any of them.

This module is read-only metadata. It does not change what
``catalog_scenarios_v26.compile_catalog_scenario`` or the v2.7 priority
previews compute, and an entry being *mapped* never implies that the event has
an effect in a projection. ``NOT_IMPLEMENTED_FAIL_CLOSED`` entries still refuse.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPING_PATH = ROOT / 'data/scenario_mapping_internal_issue8.json'
V26_REGISTRY_PATH = ROOT / 'data/scenario_contracts_v26.json'
RESEARCH_DIR = ROOT / 'research/retirepilot_2026_11_04'

INTERNAL_LABEL = 'INTERNAL_UNVALIDATED'
IMPLEMENTATION_LEVELS = (
    'LIMITED_COMPONENT',            # v2.6 bounded converter, one financial component only
    'LIMITED_PREVIEW',              # v2.7 priority preview, may not post to the projection
    'BLOCKED_PREVIEW',              # v2.7 priority entry that always refuses
    'NOT_IMPLEMENTED_FAIL_CLOSED',  # no engine; compile refuses with blockers
)


def _load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def internal_mapping() -> dict:
    """The committed Issue #8 mapping document (raises if it is missing)."""
    return _load(MAPPING_PATH)


def v26_registry() -> list[dict]:
    return _load(V26_REGISTRY_PATH)


def coverage_matrix() -> list[dict]:
    """One row per catalogue entry, separating mapped / implemented / golden / approved.

    ``golden_tested`` means an independent golden reference for the *full* event
    semantics; ``domain_approved`` means sign-off by a qualified external domain
    reviewer. Neither exists for any entry today.
    """
    mapped = {m['id']: m for m in internal_mapping()['entries']}
    rows = []
    for r in v26_registry():
        if r['previous_status'] == 'BOUNDED_OPERATOR':
            rows.append({'id': r['id'], 'name': r['name'], 'mapping_source': 'v25_bounded_operator',
                         'mapped': True, 'implemented': 'PREEXISTING_BOUNDED_OPERATOR',
                         'golden_tested': False, 'domain_approved': False,
                         'validation_status': 'PREEXISTING_NOT_EXTERNALLY_VALIDATED'})
        elif r['id'] in mapped:
            m = mapped[r['id']]
            rows.append({'id': r['id'], 'name': r['name'], 'mapping_source': 'issue8_internal',
                         'mapped': True, 'implemented': m['coverage']['implemented'],
                         'golden_tested': m['coverage']['golden_tested'],
                         'domain_approved': m['coverage']['domain_approved'],
                         'validation_status': m['validation_status']})
        else:
            rows.append({'id': r['id'], 'name': r['name'], 'mapping_source': None, 'mapped': False,
                         'implemented': None, 'golden_tested': False, 'domain_approved': False,
                         'validation_status': None})
    return rows


def _test_functions(rel: str) -> set[str]:
    path = ROOT / rel
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding='utf-8'))
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def reference_errors(doc: dict | None = None) -> list[str]:
    """Every cross-reference in the mapping must resolve; returns human-readable errors."""
    from .priority_scenarios_v27 import PRIORITY_STATUS

    doc = internal_mapping() if doc is None else doc
    registry = {r['id']: r for r in v26_registry()}
    engines = {e['ID'] for e in _load(RESEARCH_DIR / 'financial_engine_contracts_18.json')}
    decisions = {d['ID'] for d in _load(RESEARCH_DIR / 'APPROVED_PRODUCT_DECISIONS_D08_D16.json')}
    research_specs = {s['ID']: s for s in _load(RESEARCH_DIR / 'scenario_engine_contracts_46.json')}
    all_guardrails = {s['Guardrail / refusal'] for s in research_specs.values()}
    errors: list[str] = []
    seen: set[str] = set()
    for m in doc.get('entries', []):
        sid = m.get('id')
        if sid in seen:
            errors.append(f'{sid}: duplicate mapping')
        seen.add(sid)
        if sid not in registry:
            errors.append(f'{sid}: not in v2.6 catalogue registry')
            continue
        spec = research_specs.get(sid)
        if spec is None:
            errors.append(f'{sid}: not in research scenario contracts')
        else:
            expected_facts = [x.strip() for x in spec['Required facts'].split(';')]
            actual_facts = list(m.get('required_facts') or [])
            if actual_facts != expected_facts:
                extras = [f for f in actual_facts if f not in expected_facts]
                missing = [f for f in expected_facts if f not in actual_facts]
                for fact in extras:
                    errors.append(f'{sid}: dangling required fact {fact}')
                for fact in missing:
                    errors.append(f'{sid}: missing required fact {fact}')
                if not extras and not missing:
                    errors.append(f'{sid}: required_facts do not match research contract')
            actual_guardrail = m.get('guardrail')
            if actual_guardrail != spec['Guardrail / refusal']:
                if actual_guardrail not in all_guardrails:
                    errors.append(f'{sid}: dangling guardrail')
                else:
                    errors.append(f'{sid}: guardrail does not match research contract')
        reg = registry[sid]
        if reg['previous_status'] != 'UNMAPPED':
            errors.append(f'{sid}: was not one of the formerly unmapped entries')
        for key in ('name', 'category', 'execution_strategy'):
            if m.get('v26_' + key) != reg.get(key):
                errors.append(f'{sid}: v26_{key} does not match registry')
        for e in m.get('financial_engines', []):
            if e not in engines:
                errors.append(f'{sid}: unknown financial engine {e}')
        for d in m.get('applicable_decisions', []):
            if d not in decisions:
                errors.append(f'{sid}: unknown product decision {d}')
        for other in m.get('incompatible_with', []):
            if other not in registry or other == sid:
                errors.append(f'{sid}: bad incompatible_with reference {other}')
        preview = m.get('v27_priority_preview')
        if preview is not None and (preview != sid or sid not in PRIORITY_STATUS):
            errors.append(f'{sid}: v27_priority_preview does not resolve')
        level = m.get('coverage', {}).get('implemented')
        if level not in IMPLEMENTATION_LEVELS:
            errors.append(f'{sid}: unknown implementation level {level}')
        for ref in m.get('component_tests', []):
            rel, _, name = ref.partition('::')
            if name not in _test_functions(rel):
                errors.append(f'{sid}: dangling test reference {ref}')
    return errors
