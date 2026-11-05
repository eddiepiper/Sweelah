"""Synthetic-only product-library regression and fail-closed acceptance checks."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import pytest

from retirepilot.product_library import (
    load_registry, validate_registry, evaluate_product, holding_engine_inputs,
    ProductLibraryError,
)


@pytest.fixture
def registry():
    return load_registry()


@pytest.fixture
def approved_registry(registry):
    fixture = deepcopy(registry)
    sample = fixture["rules"]["rule_sets"][0]
    assert sample["product_id"] == "ocbc.account.360-account"
    sample["status"] = "approved"  # ONLY this disposable in-memory test fixture is approved
    sample["approval"] = {"reviewer": "SYNTHETIC-TEST-REVIEWER", "approved_on": "2026-11-05"}
    return fixture


def test_registry_loads_and_has_nearly_100_discovery_records(registry):
    assert len(registry["catalogue"]["products"]) == 99


def test_both_institutions_and_requested_families_present(registry):
    rows = registry["catalogue"]["products"]
    assert {p["provider"] for p in rows} == {"OCBC", "Great Eastern"}
    assert {"account", "loan", "credit_card"} <= {p["family"] for p in rows}
    assert {"life", "health", "personal_accident", "retirement_income", "wealth", "general"} <= {p["family"] for p in rows}


def test_catalogue_is_not_claimed_as_approved(registry):
    assert all(p["eligibility_verification"] == "unverified" for p in registry["catalogue"]["products"])
    assert all(p["financial_terms_verification"] == "unverified" for p in registry["catalogue"]["products"])


def test_all_products_have_registered_official_sources_and_f_engine_links(registry):
    ids = {s["id"] for s in registry["sources"]["sources"]}
    assert all(set(p["source_ids"]) <= ids for p in registry["catalogue"]["products"])
    assert all(all(x.startswith("F") and 1 <= int(x[1:]) <= 18 for x in p["engine_contracts"])
               for p in registry["catalogue"]["products"])


def test_source_checked_rules_never_execute(registry):
    result = evaluate_product("ocbc.account.360-account", {"age_years": 50},
                              "2026-11-05", registry)
    assert result["status"] == "requires_review"
    assert result["reason"] == "pending_independent_rule_approval"


def test_unknown_product_fails_closed(registry):
    result = evaluate_product("invented", {}, "2026-11-05", registry)
    assert result["reason"] == "unknown_product"


def test_product_without_rule_set_fails_closed(registry):
    result = evaluate_product("ocbc.account.ocbc-frank-account", {}, "2026-11-05", registry)
    assert result["reason"] == "no_approved_product_rules"


def test_proposal_not_effective_before_observation(registry):
    result = evaluate_product("ocbc.account.360-account", {"age_years": 50},
                              "2026-10-01", registry)
    assert result["reason"] == "no_unique_effective_rule_set"


def test_approved_synthetic_threshold_met_not_product_approval(approved_registry):
    result = evaluate_product("ocbc.account.360-account", {"age_years": 45},
                              "2026-11-05", approved_registry)
    assert result["status"] == "published_conditions_met"
    assert "Not account approval" in result["disclaimer"]
    assert "age_years" not in result  # No personal inputs echoed to logs/outputs.


def test_approved_synthetic_threshold_not_met(approved_registry):
    result = evaluate_product("ocbc.account.360-account", {"age_years": 17},
                              "2026-11-05", approved_registry)
    assert result["status"] == "published_conditions_not_met"


def test_approved_synthetic_unknown_does_not_mean_zero(approved_registry):
    result = evaluate_product("ocbc.account.360-account", {}, "2026-11-05", approved_registry)
    assert result["reason"] == "missing_customer_fact"


def test_approved_synthetic_none_does_not_mean_zero(approved_registry):
    result = evaluate_product("ocbc.account.360-account", {"age_years": None},
                              "2026-11-05", approved_registry)
    assert result["reason"] == "missing_customer_fact"


@pytest.mark.parametrize("bad", [True, False, float("inf"), float("nan"), "not a number", {}])
def test_numeric_inputs_reject_invalid_values(approved_registry, bad):
    with pytest.raises(ProductLibraryError):
        evaluate_product("ocbc.account.360-account", {"age_years": bad},
                         "2026-11-05", approved_registry)


def test_time_periods_and_overlap_fail_closed(approved_registry):
    other = deepcopy(approved_registry["rules"]["rule_sets"][0])
    other["id"] = "synthetic.overlap"
    approved_registry["rules"]["rule_sets"].append(other)
    result = evaluate_product("ocbc.account.360-account", {"age_years": 45},
                              "2026-11-05", approved_registry)
    assert result["reason"] == "no_unique_effective_rule_set"


def test_unapproved_source_cannot_be_promoted_without_review(registry):
    mutated = deepcopy(registry)
    mutated["rules"]["rule_sets"][0]["status"] = "approved"
    with pytest.raises(ProductLibraryError, match="reviewer"):
        validate_registry(mutated)


def test_unregistered_source_rejected(registry):
    mutated = deepcopy(registry)
    mutated["catalogue"]["products"][0]["source_ids"] = ["missing-source"]
    with pytest.raises(ProductLibraryError):
        validate_registry(mutated)


def test_nonofficial_source_domain_rejected(registry):
    mutated = deepcopy(registry)
    mutated["sources"]["sources"][0]["url"] = "https://ocbc.com.evil.invalid/offer"
    with pytest.raises(ProductLibraryError):
        validate_registry(mutated)


def test_duplicate_product_ids_rejected(registry):
    mutated = deepcopy(registry)
    mutated["catalogue"]["products"].append(deepcopy(mutated["catalogue"]["products"][0]))
    with pytest.raises(ProductLibraryError):
        validate_registry(mutated)


def test_unsupported_code_predicate_rejected(registry):
    mutated = deepcopy(registry)
    mutated["rules"]["rule_sets"][0]["conditions"][0]["op"] = "exec"
    with pytest.raises(ProductLibraryError):
        validate_registry(mutated)


def test_invalid_dates_rejected(registry):
    with pytest.raises(ProductLibraryError):
        evaluate_product("ocbc.account.360-account", {}, "2026-02-30", registry)


def test_unverified_contract_holding_fails_closed(registry):
    result = holding_engine_inputs("ocbc.account.360-account",
                                   {"cash_balance_sgd": "10000"}, registry)
    assert result["reason"] == "owned_contract_and_authority_evidence_required"


def test_missing_holding_value_fails_closed(registry):
    result = holding_engine_inputs("ocbc.account.360-account",
                                   {"as_of": "2026-11-05", "owner_authority_verified": True,
                                    "contract_terms_verified": True,
                                    "contract_evidence_reference": "SYNTHETIC-DOC-1"}, registry)
    assert result["reason"] == "no_verified_amounts"


def test_verified_synthetic_holding_is_only_bounded_input(registry):
    result = holding_engine_inputs("ocbc.account.360-account",
                                   {"as_of": "2026-11-05", "owner_authority_verified": True,
                                    "contract_terms_verified": True,
                                    "contract_evidence_reference": "SYNTHETIC-DOC-1",
                                    "cash_balance_sgd": "12750.25",
                                    "unconfirmed_insurance_claim_sgd": "999999"}, registry)
    assert result["status"] == "bounded_record_ready"
    assert result["confirmed_amounts"] == {"cash_balance_sgd": "12750.25"}
    assert "F14" in result["engine_contracts"]
    assert "forecast integration" in result["limitations"]


@pytest.mark.parametrize("bad", ["-5", "NaN", float("inf"), True])
def test_invalid_holding_values_rejected(registry, bad):
    with pytest.raises(ProductLibraryError):
        holding_engine_inputs("ocbc.account.360-account",
                              {"as_of": "2026-11-05", "owner_authority_verified": True,
                               "contract_terms_verified": True,
                               "contract_evidence_reference": "SYNTHETIC-DOC-1",
                               "cash_balance_sgd": bad}, registry)


def test_no_customer_data_or_hypothetical_claims_in_static_catalogue(registry):
    text = str(registry["catalogue"]["products"])
    assert "customer_email" not in text
    assert "policy_number" not in text
    assert "passport_number" not in text
