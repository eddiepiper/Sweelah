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
# Decision 7A: no evidence. Stored as JSON null (QA G5 on 8e812e0 found the
# accidental string "None", a Python str(None) style leak; fixed to null).
EVIDENCE_NONE = None
LABEL_VALUE_FIELDS = (
    "life_stage", "work_income_type", "cpf_retirement_situation",
    "household_context", "planning_complexity",
)
# Canonical SHA-256 of [[persona_id, <5 label values>], ...] for the 96 records
# at 8e812e0, the file the Head of Product signed off as a Product draft
# (480 values). Must not move.
HOP_SIGNED_VALUES_SHA256 = "4ddbbf3bb652574ade18c4b842c91f4c6f55799251162b4b3d57c102fb5d5767"
# Canonical SHA-256 of the whole 8e812e0 document with every evidence_level key
# removed. Proves evidence_level is the only field that changed since sign-off.
HOP_SIGNED_DOC_WITHOUT_EVIDENCE_SHA256 = "324631c63b9120bc0d30b301f128acd4462de54c7d5a03bcd2ef3835883c443b"

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
# Needles with every non-alphanumeric character removed and lower-cased, so a
# split or concatenated reference ("persona_draft_" + "labels",
# "_".join(["persona", "draft", "labels"]), adjacent string literals) is caught.
COLLAPSED_NEEDLES = tuple(sorted({re.sub(r"[^a-z0-9]", "", n.lower()) for n in NEEDLES}))
SCANNED_SUFFIXES = {".py", ".html", ".htm", ".js", ".mjs", ".css", ".json", ".txt", ".md", ".toml", ".yaml", ".yml"}
FORBIDDEN_FIELD_RE = re.compile(
    r"(score|weight|percent|percentage|confidence|probability|match_score|risk_tier|risk-tier)",
    re.I,
)
# Applied to keys normalised to lower-case alphanumerics, so camelCase,
# PascalCase, kebab, dotted and spaced variants ("riskTier", "Risk Tier",
# "risk.tier", "matchScore") are caught too.
FORBIDDEN_COLLAPSED_KEY_RE = re.compile(
    r"(score|weight|percent|confidence|probability|risktier|riskrating|risklevel|riskgrade|riskband)"
)
NEEDS_HOP_REVIEW_RE = re.compile(r"needs\s+(head\s+of\s+product|hop)\s+review", re.I)
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


def _collapse(text: str) -> str:
    """Lower-case and drop every non-alphanumeric character."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _isolation_hits(paths, root=ROOT):
    """Report files that reference the labels file, literally or split up."""
    hits = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in NEEDLES:
            if needle in text:
                hits.append(f"{rel} contains {needle!r}")
        collapsed = _collapse(text)
        for needle in COLLAPSED_NEEDLES:
            if needle in collapsed:
                hits.append(f"{rel} contains a split or concatenated {needle!r}")
    return hits


def _package_files(package_dir: Path):
    """Every scannable file under package_dir, including subpackages."""
    return sorted(
        p for p in package_dir.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix.lower() in SCANNED_SUFFIXES
    )


def _forbidden_key_paths(obj, path="$"):
    out = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}"
            if FORBIDDEN_COLLAPSED_KEY_RE.search(_collapse(key)):
                out.append(here)
            out.extend(_forbidden_key_paths(value, here))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            out.extend(_forbidden_key_paths(value, f"{path}[{i}]"))
    return out


def _needs_hop_review_hits(records):
    hits = []
    for rec in records:
        for field, value in rec.items():
            if isinstance(value, str):
                flat = " ".join(value.replace("\u00a0", " ").replace("-", " ").split())
                if NEEDS_HOP_REVIEW_RE.search(flat):
                    hits.append(f"{rec.get('persona_id')}.{field}")
    return hits


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
    assert row["evidence_level"] is EVIDENCE_NONE
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


# Head of Product review (AT-PROD-SW3, Status: Proposed) of c32ede1:
# 475 of 480 values accepted; these five field values must change.
HOP_VALUE_CORRECTIONS = [
    ("A06", "cpf_retirement_situation", "accumulating"),
    ("A08", "cpf_retirement_situation", "payout_started"),
    ("A03", "planning_complexity", "standard"),
    ("A04", "planning_complexity", "standard"),
    ("K02", "planning_complexity", "specialist_review_suggested"),
]
# Enum and identity fields that must otherwise match c32ede1 exactly.
FROZEN_RECORD_FIELDS = (
    "persona_id", "family", "name", "life_stage", "work_income_type",
    "cpf_retirement_situation", "household_context", "planning_complexity",
    "label_status", "evidence_level",
)
# Rationale / reason text may change only on the corrected records and on the
# G-7 hygiene edits (E02, K06, K07).
ALLOWED_TEXT_EDITS = {
    "A03": {"planning_complexity_reason"},
    "A04": {"planning_complexity_reason"},
    "A06": {"rationale"},
    "A08": {"rationale"},
    "K02": {"planning_complexity_reason"},
    "E02": {"rationale"},
    "K06": {"rationale"},
    "K07": {"rationale"},
}
# Byte-identical committed copy of c32ede1:data/persona_draft_labels_issue3.json
# (the file HoP reviewed). Used instead of `git show` so the test does not need
# git history: CI checks out with depth 1 (QA G5 on 8e812e0, condition 1).
C32EDE1_SNAPSHOT = ROOT / "tests/fixtures/issue3/persona_draft_labels_issue3_c32ede1.json"
C32EDE1_SNAPSHOT_SHA256 = "ceec1f434d280d99406cc41e3e3e374042bb3c20cf792b9be22d73d202b11de4"
# The only value transform allowed on top of the HoP corrections since c32ede1:
# evidence_level string "None" -> JSON null.
EVIDENCE_LEVEL_TRANSFORM = ("None", None)


def _c32ede1_labels():
    raw = C32EDE1_SNAPSHOT.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == C32EDE1_SNAPSHOT_SHA256
    return json.loads(raw.decode("utf-8"))


def _row(pid):
    return next(r for r in _records() if r["persona_id"] == pid)


@pytest.mark.parametrize("pid,field,expected", HOP_VALUE_CORRECTIONS)
def test_hop_review_corrections_are_applied(pid, field, expected):
    assert _row(pid)[field] == expected


def test_a08_rationale_matches_payout_started_consistent_with_peers():
    row = _row("A08")
    text = row["rationale"]
    assert row["cpf_retirement_situation"] == "payout_started"
    assert "cpf_income" in text
    assert "payout_started" in text
    for peer in ("B08", "G08", "I07", "L03", "L04"):
        assert peer in text, f"A08 rationale should cite {peer}"
    assert "varies" not in text


def test_k02_complexity_reason_cites_foreign_pension_and_peer_pattern():
    row = _row("K02")
    reason = row["planning_complexity_reason"]
    assert row["planning_complexity"] == "specialist_review_suggested"
    assert "foreign_pension" in reason
    assert "overseas_assets" in reason
    assert "K06" in reason or "K08" in reason


def test_g7_rationales_do_not_say_needs_head_of_product_review():
    blob = " ".join(_row(pid)["rationale"] for pid in ("E02", "K06", "K07"))
    assert "needs Head of Product review" not in blob
    assert "needs head of product review" not in blob.lower()


def test_only_hop_allowed_record_fields_differ_from_c32ede1():
    old_by_id = {r["persona_id"]: r for r in _c32ede1_labels()["records"]}
    new_by_id = {r["persona_id"]: r for r in _records()}
    assert set(old_by_id) == set(new_by_id) == set(_rules()["personas"])
    unexpected = []
    expected_value_changes = {(pid, field) for pid, field, _ in HOP_VALUE_CORRECTIONS}
    for pid, old in old_by_id.items():
        new = new_by_id[pid]
        assert set(old) == set(new) == set(RECORD_KEYS)
        for field in FROZEN_RECORD_FIELDS:
            if field == "evidence_level" and (old[field], new[field]) == EVIDENCE_LEVEL_TRANSFORM:
                continue
            if old[field] != new[field] and (pid, field) not in expected_value_changes:
                unexpected.append(f"{pid}.{field}: {old[field]!r} -> {new[field]!r}")
        for field in ("planning_complexity_reason", "rationale"):
            if old[field] != new[field] and field not in ALLOWED_TEXT_EDITS.get(pid, set()):
                unexpected.append(f"{pid}.{field} changed without HoP leave")
    for pid, field, expected in HOP_VALUE_CORRECTIONS:
        assert old_by_id[pid][field] != expected
        assert new_by_id[pid][field] == expected
    assert unexpected == [], "unexpected record changes vs c32ede1:\n" + "\n".join(unexpected)


def test_planning_complexity_reasons_stay_internal_only():
    """Decision 3A: complexity reasons (for example L08 'protective referral')
    must not appear in the consumer UI, API, exports or the assistant."""
    doc = _labels()
    header = json.dumps({k: v for k, v in doc.items() if k != "records"})
    lowered = header.lower()
    assert "planning_complexity_reason" in lowered or "protective referral" in lowered
    assert "internal" in lowered
    assert "3A" in header
    assert any(word in lowered for word in ("consumer", "ui", "api", "export", "assistant"))

    reasons = [rec["planning_complexity_reason"] for rec in _records()]
    assert any("protective referral" in reason for reason in reasons)
    needles = list(NEEDLES) + ["protective referral"] + reasons
    hits = []
    for rel in CONSUMER_PATHS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle and needle in text:
                hits.append(f"{rel} contains {needle!r}")
    assert hits == [], "complexity reasons or the labels file leaked into a consumer path:\n" + "\n".join(hits)


# ---- QA G5 on 8e812e0: conditions (history-free snapshot, evidence_level, test gaps)


def test_c32ede1_snapshot_is_committed_and_pinned():
    assert C32EDE1_SNAPSHOT.is_file(), f"missing {C32EDE1_SNAPSHOT}"
    assert hashlib.sha256(C32EDE1_SNAPSHOT.read_bytes()).hexdigest() == C32EDE1_SNAPSHOT_SHA256
    assert len(_c32ede1_labels()["records"]) == 96


def test_evidence_level_is_json_null_not_the_string_none():
    doc = _labels()
    assert "evidence_level" in doc and doc["evidence_level"] is None
    assert all("evidence_level" in r and r["evidence_level"] is None for r in doc["records"])
    raw = LABELS_PATH.read_text(encoding="utf-8")
    assert '"evidence_level": "None"' not in raw
    assert raw.count('"evidence_level": null') == 97


def test_hop_signed_label_values_unchanged_since_8e812e0():
    values = [[r["persona_id"]] + [r[f] for f in LABEL_VALUE_FIELDS] for r in _records()]
    assert sum(len(v) - 1 for v in values) == 480
    assert hashlib.sha256(_canon(values)).hexdigest() == HOP_SIGNED_VALUES_SHA256


def test_only_evidence_level_changed_since_hop_signed_8e812e0():
    doc = _labels()
    stripped = {k: v for k, v in doc.items() if k != "evidence_level"}
    stripped["records"] = [
        {k: v for k, v in r.items() if k != "evidence_level"} for r in doc["records"]
    ]
    assert hashlib.sha256(_canon(stripped)).hexdigest() == HOP_SIGNED_DOC_WITHOUT_EVIDENCE_SHA256


def test_labels_not_referenced_anywhere_under_retirepilot_including_subpackages():
    """C6 + C7: recursive scan, and split or concatenated references."""
    files = _package_files(ROOT / "retirepilot")
    assert any(p.name == "api.py" for p in files)
    hits = _isolation_hits(files)
    assert hits == [], "draft labels referenced from retirepilot/:\n" + "\n".join(hits)


def test_consumer_paths_have_no_split_or_concatenated_labels_reference():
    """C7 on the explicit consumer list (api, service, ui, assistant, ...)."""
    hits = _isolation_hits([ROOT / rel for rel in CONSUMER_PATHS])
    assert hits == [], "draft labels referenced from a consumer path:\n" + "\n".join(hits)


@pytest.mark.parametrize("snippet", [
    'LABELS = "persona_draft_" + "labels_issue3.json"\n',
    'LABELS = ("persona_draft"\n          "_labels_issue3.json")\n',
    'LABELS = "_".join(["persona", "draft", "labels"])\n',
    'const f = `persona_draft_${"labels"}`;\n',
    'STATUS = "DRAFT_NOT_" + "INDEPENDENTLY_REVIEWED"\n',
])
def test_isolation_scan_catches_split_references_in_a_subpackage(tmp_path, snippet):
    """Guards the scanner itself: a reader in a nested subpackage that splits
    the filename must be reported."""
    pkg = tmp_path / "retirepilot" / "plugins" / "nested"
    pkg.mkdir(parents=True)
    (tmp_path / "retirepilot" / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "reader.py").write_text(snippet, encoding="utf-8")
    hits = _isolation_hits(_package_files(tmp_path / "retirepilot"), root=tmp_path)
    assert hits, f"scanner missed {snippet!r}"
    assert all("retirepilot/plugins/nested/reader.py" in h for h in hits)


def test_collapsed_needles_do_not_flag_unrelated_text():
    clean = 'path = "data/personas.json"  # draft labels for UI copy\n'
    assert _isolation_hits_text(clean) == []


def _isolation_hits_text(text: str):
    collapsed = _collapse(text)
    return [n for n in NEEDLES if n in text] + [n for n in COLLAPSED_NEEDLES if n in collapsed]


def test_no_risk_tier_or_score_key_in_any_case_style():
    """B4: riskTier, RiskTier, risk.tier, 'risk tier' and similar keys."""
    doc = _labels()
    assert _forbidden_key_paths(doc) == []
    collapsed_blob = _collapse(json.dumps(doc).replace("No risk tier", " "))
    assert "risktier" not in collapsed_blob


@pytest.mark.parametrize("key", [
    "riskTier", "RiskTier", "risk_tier", "risk-tier", "risk.tier", "Risk Tier",
    "RISK_TIER", "riskLevel", "riskRating", "matchScore", "confidencePct",
])
def test_forbidden_key_check_catches_case_variants(key):
    record = {"persona_id": "A01", key: "low"}
    assert _forbidden_key_paths({"records": [record]}) == [f"$.records[0].{key}"]


def test_no_record_says_needs_head_of_product_review():
    """E2/E3: every string field of all 96 records, not only E02/K06/K07."""
    records = _records()
    assert len(records) == 96
    hits = _needs_hop_review_hits(records)
    assert hits == [], "records still say they need HoP review: " + ", ".join(hits)


@pytest.mark.parametrize("text", [
    "needs Head of Product review",
    "Needs head of product review.",
    "needs  Head\u00a0of Product review",
    "needs Head-of-Product review",
    "needs HoP review",
])
def test_needs_hop_review_check_catches_variants(text):
    rec = {"persona_id": "A01", "planning_complexity_reason": f"Something; {text}"}
    assert _needs_hop_review_hits([rec]) == ["A01.planning_complexity_reason"]
