"""Source-traceable product discovery and bounded eligibility evaluation for SweeLah.

Never treats a marketing listing as an entitlement, credit decision, insurance
acceptance, financial recommendation or a policy-specific benefit. No PII is stored.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent / "product_library"
ALLOWED_PROVIDERS = {"OCBC", "Great Eastern"}
ALLOWED_HOSTS = {"www.ocbc.com", "ocbc.com", "www.greateasternlife.com", "greateasternlife.com"}
ALLOWED_RULE_STATES = {"candidate", "source_checked", "approved", "retired"}
ALLOWED_OPERATORS = {"eq", "in", "gt", "gte", "lt", "lte"}
NUMERIC_FACTS = {"age_years", "annual_income_sgd", "initial_deposit_sgd",
                 "salary_credit_sgd", "single_premium_sgd"}
FACTS = NUMERIC_FACTS | {"residency", "dps_policyholder", "existing_base_policy"}
BRIDGE_AMOUNTS = {"cash_balance_sgd", "loan_balance_sgd", "monthly_loan_payment_sgd",
                  "monthly_premium_sgd"}


class ProductLibraryError(ValueError):
    pass


def _day(value, field):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ProductLibraryError(f"{field}: valid ISO calendar date required") from None


def _amount(value, field):
    if isinstance(value, bool) or value is None:
        raise ProductLibraryError(f"{field}: decimal value required")
    try:
        result = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        raise ProductLibraryError(f"{field}: invalid decimal") from None
    if not result.is_finite():
        raise ProductLibraryError(f"{field}: non-finite decimal")
    return result


def load_registry(root=None):
    """Load local, repository-versioned reference data only; makes no web requests."""
    directory = Path(root) if root is not None else ROOT
    with (directory / "products_v1.json").open(encoding="utf-8") as stream:
        catalogue = json.load(stream)
    with (directory / "sources_v1.json").open(encoding="utf-8") as stream:
        sources = json.load(stream)
    with (directory / "rules_v1.json").open(encoding="utf-8") as stream:
        rules = json.load(stream)
    registry = {"catalogue": catalogue, "sources": sources, "rules": rules}
    validate_registry(registry)
    return registry


def validate_registry(registry):
    """Validate provenance, unique IDs, references and basic effective dates."""
    try:
        catalogue, sources, rules = (registry[k] for k in ("catalogue", "sources", "rules"))
        products = catalogue["products"]
        citations = sources["sources"]
        rule_sets = rules["rule_sets"]
        versions = [catalogue["version"], sources["version"], rules["version"]]
    except (KeyError, TypeError) as error:
        raise ProductLibraryError(f"Missing registry field: {error}") from None
    if not all(isinstance(x, str) and x for x in versions):
        raise ProductLibraryError("Registry version is required")
    _day(catalogue["catalogue_as_of"], "catalogue_as_of")
    product_ids, source_ids, ruleset_ids = set(), set(), set()
    for source in citations:
        sid = source["id"]
        if sid in source_ids:
            raise ProductLibraryError(f"Duplicate source ID: {sid}")
        source_ids.add(sid)
        uri = urlparse(source["url"])
        if uri.scheme != "https" or uri.hostname not in ALLOWED_HOSTS:
            raise ProductLibraryError(f"Source URL outside approved official domains: {sid}")
        _day(source["checked_on"], "checked_on")
    for product in products:
        pid = product["id"]
        if pid in product_ids:
            raise ProductLibraryError(f"Duplicate product ID: {pid}")
        product_ids.add(pid)
        if product["provider"] not in ALLOWED_PROVIDERS or product["market"] != "SG":
            raise ProductLibraryError(f"Unsupported provider/market: {pid}")
        if not product.get("name") or not product.get("family"):
            raise ProductLibraryError(f"Missing product identity: {pid}")
        if not product.get("source_ids") or not set(product["source_ids"]) <= source_ids:
            raise ProductLibraryError(f"Product requires registered official sources: {pid}")
        if product.get("eligibility_verification") != "unverified":
            raise ProductLibraryError(f"Catalogue cannot claim rule approval: {pid}")
    for ruleset in rule_sets:
        rid = ruleset["id"]
        if rid in ruleset_ids:
            raise ProductLibraryError(f"Duplicate rule set: {rid}")
        ruleset_ids.add(rid)
        if ruleset["product_id"] not in product_ids:
            raise ProductLibraryError(f"Rule set references unknown product: {rid}")
        if ruleset["status"] not in ALLOWED_RULE_STATES:
            raise ProductLibraryError(f"Invalid rule state: {rid}")
        first = _day(ruleset["effective_from"], "effective_from")
        last = ruleset.get("effective_to")
        if last and _day(last, "effective_to") < first:
            raise ProductLibraryError(f"Invalid rule period: {rid}")
        if not ruleset["source_ids"] or not set(ruleset["source_ids"]) <= source_ids:
            raise ProductLibraryError(f"Missing source link: {rid}")
        if not ruleset.get("conditions"):
            raise ProductLibraryError(f"Rule conditions required: {rid}")
        for condition in ruleset["conditions"]:
            if condition.get("field") not in FACTS or condition.get("op") not in ALLOWED_OPERATORS:
                raise ProductLibraryError(f"Unsupported predicate in {rid}")
            if "value" not in condition:
                raise ProductLibraryError(f"Missing predicate value in {rid}")
        if ruleset["status"] == "approved":
            approval = ruleset.get("approval") or {}
            if not approval.get("reviewer") or not approval.get("approved_on"):
                raise ProductLibraryError(f"Approved rule requires accountable reviewer: {rid}")
            if _day(approval["approved_on"], "approved_on") < first:
                raise ProductLibraryError(f"Approval cannot precede rule start: {rid}")
    return True


def _predicate(condition, facts):
    field, op, target = condition["field"], condition["op"], condition["value"]
    if field not in facts or facts[field] is None:
        return None
    actual = facts[field]
    if field in NUMERIC_FACTS:
        left, right = _amount(actual, field), _amount(target, f"rule.{field}")
    else:
        if not isinstance(actual, (str, bool)):
            raise ProductLibraryError(f"{field}: string or boolean expected")
        left, right = actual, target
    if op == "eq":
        return left == right
    if op == "in":
        if not isinstance(target, list) or field in NUMERIC_FACTS:
            raise ProductLibraryError("in requires a non-numeric options list")
        return left in target
    if field not in NUMERIC_FACTS:
        raise ProductLibraryError("Ordering predicates must compare numeric facts")
    return {"gt": left > right, "gte": left >= right,
            "lt": left < right, "lte": left <= right}[op]


def evaluate_product(product_id, facts, as_of, registry=None):
    """Evaluate only approved source-backed predicates.

    Outcomes describe *published conditions*, never final customer eligibility.
    Unknown facts, incomplete coverage, non-approved rules or time conflicts fail closed.
    Caller must not pass real personal data to a shared or logged test environment.
    """
    if not isinstance(facts, dict):
        raise ProductLibraryError("facts must be an object")
    requested = _day(as_of, "as_of")
    data = registry if registry is not None else load_registry()
    validate_registry(data)
    products = {p["id"]: p for p in data["catalogue"]["products"]}
    product = products.get(product_id)
    base = {"product_id": product_id, "as_of": as_of,
            "catalogue_version": data["catalogue"]["version"],
            "status": "requires_review"}
    if product is None:
        return {**base, "reason": "unknown_product", "rule_ids": []}
    applicable = [r for r in data["rules"]["rule_sets"] if r["product_id"] == product_id]
    if not applicable:
        return {**base, "reason": "no_approved_product_rules", "rule_ids": []}
    active = [r for r in applicable if
              _day(r["effective_from"], "effective_from") <= requested and
              (not r.get("effective_to") or requested <= _day(r["effective_to"], "effective_to"))]
    if len(active) != 1:
        return {**base, "reason": "no_unique_effective_rule_set", "rule_ids": []}
    rule = active[0]
    metadata = {"rule_ids": [rule["id"]], "source_ids": rule["source_ids"],
                "rule_status": rule["status"], "rules_version": data["rules"]["version"]}
    if rule["status"] != "approved":
        return {**base, **metadata, "reason": "pending_independent_rule_approval"}
    # Explicitly treat rule coverage as bounded, not a complete credit/insurance decision.
    if rule.get("coverage") != "published_thresholds_only":
        return {**base, **metadata, "reason": "unsupported_rule_coverage"}
    answers = [_predicate(c, facts) for c in rule["conditions"]]
    if None in answers:
        return {**base, **metadata, "reason": "missing_customer_fact"}
    if not all(answers):
        return {**base, **metadata, "status": "published_conditions_not_met",
                "reason": "one_or_more_thresholds_not_met",
                "disclaimer": "Other approval conditions, exceptions and underwriting not assessed"}
    return {**base, **metadata, "status": "published_conditions_met",
            "reason": "limited_published_conditions_met",
            "disclaimer": "Not account approval, credit approval, insurance acceptance or advice"}


def holding_engine_inputs(product_id, holding, registry=None):
    """Bounded bridge to existing F01-F18 engine contracts, never an inferred payout.

    Returns only explicitly documented monetary facts for a customer-owned holding.
    This is NOT yet wired into the main forecast, and does not persist any data.
    """
    data = registry if registry is not None else load_registry()
    validate_registry(data)
    matching = next((p for p in data["catalogue"]["products"] if p["id"] == product_id), None)
    if matching is None:
        return {"status": "requires_review", "reason": "unknown_product"}
    if not isinstance(holding, dict):
        raise ProductLibraryError("holding must be an object")
    if (holding.get("owner_authority_verified") is not True or
        holding.get("contract_terms_verified") is not True or
        not holding.get("contract_evidence_reference")):
        return {"status": "requires_review", "reason": "owned_contract_and_authority_evidence_required"}
    _day(holding.get("as_of"), "holding.as_of")
    amounts = {}
    for key in BRIDGE_AMOUNTS:
        if key in holding:
            value = _amount(holding[key], key)
            if value < 0:
                raise ProductLibraryError(f"{key}: negative amount forbidden")
            amounts[key] = str(value)
    if not amounts:
        return {"status": "requires_review", "reason": "no_verified_amounts"}
    return {"status": "bounded_record_ready", "product_id": product_id,
            "as_of": holding["as_of"], "engine_contracts": matching["engine_contracts"],
            "confirmed_amounts": amounts,
            "limitations": "No forecast integration, claim entitlement, inferred benefits or rate assumptions"}
