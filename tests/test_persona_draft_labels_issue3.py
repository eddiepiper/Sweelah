"""SWEELAH-ISSUE-3 (Refs #3): internal draft persona labels.

The labels are a Product-owned first pass, marked DRAFT and not independently
reviewed. They must not be imported by or exposed via the consumer UI, API or
exports, and must not change matching gates, weights or results.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from retirepilot.adapter import classify_household
from retirepilot.service import evaluate

ROOT = Path(__file__).resolve().parent.parent
LABELS_PATH = ROOT / "data/persona_draft_labels_issue3.json"
RULES_PATH = ROOT / "retirepilot/retirepilot_rules_v1.2.json"
# SHA-256 of retirepilot/retirepilot_rules_v1.2.json on origin/main (823ef72).
RULES_SHA256 = "3e0fed7a0fb751ccfe9b857a51404dc1a26f29634cea9ae77c73e6fba913ec4b"

LIFE_STAGES = frozenset({
    "pre_retirement_45_54", "near_retirement_55_64", "payout_age_65_plus", "spans_stages",
})
WORK_INCOME_TYPES = frozenset({
    "salaried", "platform_gig", "self_employed_or_commission", "not_working",
    "mixed", "not_applicable",
})
CPF_SITUATIONS = frozenset({
    "accumulating", "approaching_55_ra_formation", "payout_started",
    "payout_deferred", "limited_or_no_cpf", "varies",
})
HOUSEHOLD_CONTEXTS = frozenset({
    "single", "couple", "dependants", "caregiver", "multi_generation", "varies",
})
PLANNING_COMPLEXITIES = frozenset({
    "standard", "elevated", "specialist_review_suggested",
})
RECORD_KEYS = (
    "persona_id", "family", "name", "life_stage", "work_income_type",
    "cpf_retirement_situation", "household_context", "planning_complexity",
    "planning_complexity_reason", "label_status", "evidence_level", "rationale",
)
DRAFT_STATUS = "DRAFT_NOT_INDEPENDENTLY_REVIEWED"
EVIDENCE_NONE = "None"

# Canonical SHA-256 of classify_household(...) and of evaluate(...)["classification"]
# for the three shipped synthetic households on origin/main (823ef72), using
# json.dumps(..., sort_keys=True, separators=(",", ":")).
HOUSEHOLD_CLASSIFY_SHA256 = {
    "salaried_household.json": "00bd956323b347f8ef17f5a034097c0aff22edbce6b6860f245507d7f5a81e6f",
    "retired_household.json": "cc3ae3aa4572795606751d113e4cc9c50daddd3f50006f2f4a90f6205936321f",
    "mixed_income_household.json": "55ba75d5b793fa34a1054d8be388429752f369159d73ced44adbb76055c9ff5c",
}
HOUSEHOLD_PUBLIC_SHA256 = {
    "salaried_household.json": "61ae4c9798e80d6fcaefbba6f4aaddb364cba58b15d6f9c30e255ae2a7aeac36",
    "retired_household.json": "35cf4d845b75c7f3f1096aef1d39b8bdb9e8b759508a1b54e937a6cbe20fd256",
    "mixed_income_household.json": "4b32a1533385f50badf9f74a2b6c1fea3f915ceedf0584370ec80b656f1cbdca",
}

CONSUMER_PATHS = [
    "retirepilot/api.py",
    "retirepilot/service.py",
    "retirepilot/ui.html",
    "retirepilot/assistant.py",
    "retirepilot/s016.html",
    "retirepilot/cli.py",
    "retirepilot/adapter.py",
    "retirepilot/core.py",
    "retirepilot/classifier_legacy.py",
    "retirepilot/policy.py",
    "retirepilot/product_library.py",
    "retirepilot/planner_session_v24.py",
    "retirepilot/llm_adapter.py",
    "retirepilot/projection_v22.py",
    "retirepilot/statutory_2026.py",
    "retirepilot/cpf_retirement_v26.py",
    "retirepilot/priority_scenarios_v27.py",
    "retirepilot/catalog_scenarios_v26.py",
]
NEEDLES = (
    "persona_draft_labels_issue3",
    "persona_draft_labels",
    "DRAFT_NOT_INDEPENDENTLY_REVIEWED",
)
FORBIDDEN_FIELD_RE = re.compile(
    r"(score|weight|percent|percentage|confidence|probability|match_score|risk_tier|risk-tier)",
    re.I,
)
BARE_NUMBER_RE = re.compile(r"^[-+]?\d+(\.\d+)?$")


def _rules():
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def _labels():
    return json.loads(LABELS_PATH.read_text(encoding="utf-8"))


def _records():
    doc = _labels()
    assert "records" in doc, "labels file is missing a top-level records list"
    return doc["records"]


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _allowed_digit_tokens(rules) -> set[str]:
    """Identifiers that may contain digits: taxonomy enums, rules fields
    copied verbatim, decision ids, and document citations. Not scores."""
    tokens = {
        "pre_retirement_45_54",
        "near_retirement_55_64",
        "payout_age_65_plus",
        "approaching_55_ra_formation",
        "v2.7",
        "PSD v2.7",
        "section 3",
        "Appendix A",
        "SWEELAH-ISSUE-3",
        "Refs #3",
        "#3",
        "1A",
        "2A",
        "3A",
        "7A",
        "D-001",
        "D-002",
        "D-003",
        "D-007",
        "None",
        "v1.2",
        "retirepilot_rules_v1.2.json",
        "retirepilot/retirepilot_rules_v1.2.json",
        "APPROVED_DECISIONS_v2.7.md",
        "docs/APPROVED_DECISIONS_v2.7.md",
        "persona_draft_labels_issue3.json",
        "data/persona_draft_labels_issue3.json",
        "build_persona_draft_labels_issue3.py",
        "scripts/build_persona_draft_labels_issue3.py",
    }
    personas = rules["personas"]
    tokens.update(personas)
    for rec in personas.values():
        tokens.add(rec["id"])
        tokens.add(rec["gate"])
        tokens.add(rec.get("exclusion", ""))
        tokens.add(rec["name"])
        tokens.add(rec["family"])
        tokens.add(rec["planning_focus"])
        for crit in rec["criteria"]:
            tokens.add(crit["predicate"])
            tokens.add(crit["dimension"])
    return {t for t in tokens if t and any(ch.isdigit() for ch in t)}


def _digit_runs_not_covered(text: str, allowed_tokens: set[str]) -> list[str]:
    """Return digit-containing slices of text that are not part of an allowed token."""
    # Mask allowed tokens (longest first) so leftover digits can be flagged.
    masked = text
    for token in sorted(allowed_tokens, key=len, reverse=True):
        if token and token in masked:
            masked = masked.replace(token, " " * len(token))
    return [m.group(0) for m in re.finditer(r"\S*\d\S*", masked)]


def test_rules_file_hash_is_unchanged():
    assert hashlib.sha256(RULES_PATH.read_bytes()).hexdigest() == RULES_SHA256


def test_labels_file_exists_and_header_marks_internal_draft():
    assert LABELS_PATH.is_file(), f"missing {LABELS_PATH}"
    doc = _labels()
    blob = {k: v for k, v in doc.items() if k != "records"}
    text = json.dumps(blob)
    lowered = text.lower()
    assert "internal" in lowered and "draft" in lowered
    assert "product" in lowered
    assert "head of product" in lowered
    assert "pending" in lowered and "review" in lowered
    assert DRAFT_STATUS in text
    for decision in ("1A", "2A", "3A", "7A"):
        assert decision in text, f"header must cite decision {decision}"


def test_exactly_96_unique_ids_matching_the_rules_file():
    rules = _rules()
    records = _records()
    rule_ids = list(rules["personas"])
    label_ids = [r["persona_id"] for r in records]
    assert len(rule_ids) == 96
    assert len(label_ids) == 96
    assert len(set(label_ids)) == 96
    assert label_ids == rule_ids


@pytest.mark.parametrize("pid", json.loads(RULES_PATH.read_text())["personas"])
def test_family_and_name_identical_to_rules(pid):
    rec = _rules()["personas"][pid]
    row = next(r for r in _records() if r["persona_id"] == pid)
    assert row["family"] == rec["family"]
    assert row["name"] == rec["name"]


@pytest.mark.parametrize("pid", json.loads(RULES_PATH.read_text())["personas"])
def test_every_value_is_in_its_enum_and_draft_fields_are_present(pid):
    row = next(r for r in _records() if r["persona_id"] == pid)
    assert tuple(row.keys()) == RECORD_KEYS
    assert row["life_stage"] in LIFE_STAGES
    assert row["work_income_type"] in WORK_INCOME_TYPES
    assert row["cpf_retirement_situation"] in CPF_SITUATIONS
    assert row["household_context"] in HOUSEHOLD_CONTEXTS
    assert row["planning_complexity"] in PLANNING_COMPLEXITIES
    assert row["label_status"] == DRAFT_STATUS
    assert row["evidence_level"] == EVIDENCE_NONE
    assert row["rationale"].strip()
    assert row["planning_complexity_reason"].strip()
    assert "\n" not in row["rationale"]
    assert "\n" not in row["planning_complexity_reason"]


def test_no_risk_tier_field():
    """HoP and decision 1A: do not add a risk tier. The header may say so."""
    doc = _labels()
    offenders = []

    def walk(obj, path):
        if isinstance(obj, dict):
            for key, value in obj.items():
                here = f"{path}.{key}"
                normalised = key.lower().replace("-", "_")
                if normalised == "risk_tier":
                    offenders.append(here)
                walk(value, here)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{path}[{i}]")

    walk(doc, "$")
    assert offenders == [], "risk_tier field is not part of the taxonomy: " + ", ".join(offenders)
    blob = json.dumps(doc).lower()
    assert "risk_tier" not in blob
    assert "risk-tier" not in blob
    # Prose may state the prohibition ("No risk tier") but must not assign one.
    leftover = blob.replace("no risk tier", " ")
    assert "risk tier" not in leftover


def test_no_numeric_fields_or_score_like_values():
    doc = _labels()
    rules = _rules()
    allowed = _allowed_digit_tokens(rules)
    offenders = []

    def walk(obj, path):
        if isinstance(obj, dict):
            for key, value in obj.items():
                here = f"{path}.{key}"
                if FORBIDDEN_FIELD_RE.search(key):
                    offenders.append(f"forbidden field name {here}")
                walk(value, here)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{path}[{i}]")
        elif isinstance(obj, bool) or obj is None:
            return
        elif isinstance(obj, (int, float)):
            offenders.append(f"numeric JSON value at {path}: {obj!r}")
        elif isinstance(obj, str):
            if "%" in obj:
                offenders.append(f"percent sign at {path}: {obj!r}")
            if BARE_NUMBER_RE.fullmatch(obj.strip()):
                offenders.append(f"bare numeric string at {path}: {obj!r}")
            leftover = _digit_runs_not_covered(obj, allowed)
            # Allow the path-like filename and the word JSON itself; leftover
            # tokens are score-like if they still contain digits.
            for token in leftover:
                offenders.append(f"digits used outside allowed identifiers at {path}: {token!r} in {obj!r}")
        else:
            offenders.append(f"unsupported JSON type at {path}: {type(obj).__name__}")

    walk(doc, "$")
    assert offenders == [], "\n".join(offenders)


def test_labels_file_is_not_referenced_by_consumer_paths():
    hits = []
    for rel in CONSUMER_PATHS:
        path = ROOT / rel
        assert path.is_file(), f"expected consumer path missing: {rel}"
        text = path.read_text(encoding="utf-8")
        for needle in NEEDLES:
            if needle in text:
                hits.append(f"{rel} contains {needle!r}")
    assert hits == [], "draft labels leaked into a consumer path:\n" + "\n".join(hits)


def test_labels_filename_not_imported_under_retirepilot_package():
    hits = []
    for path in sorted((ROOT / "retirepilot").glob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".html", ".js", ".css", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in NEEDLES:
            if needle in text:
                hits.append(f"retirepilot/{path.name} contains {needle!r}")
    assert hits == [], "draft labels referenced from retirepilot/:\n" + "\n".join(hits)


@pytest.mark.parametrize("filename", sorted(HOUSEHOLD_CLASSIFY_SHA256))
def test_shipped_household_matching_results_unchanged(filename):
    profile = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    raw = classify_household(profile)
    public = evaluate(profile, [], 10)["classification"]
    assert hashlib.sha256(_canon(raw)).hexdigest() == HOUSEHOLD_CLASSIFY_SHA256[filename]
    assert hashlib.sha256(_canon(public)).hexdigest() == HOUSEHOLD_PUBLIC_SHA256[filename]
    assert public["evaluated"] == 96
    assert all(item["status"] == "provisional_pattern" for item in public["user_visible_top_three"])

def test_generator_reproduces_the_committed_file(tmp_path):
    import subprocess
    import sys
    script = ROOT / "scripts/build_persona_draft_labels_issue3.py"
    dest = tmp_path / "persona_draft_labels_issue3.json"
    subprocess.check_call([sys.executable, str(script), str(dest)])
    assert dest.read_bytes() == LABELS_PATH.read_bytes()
